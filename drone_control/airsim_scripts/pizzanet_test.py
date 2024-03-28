### Imports and Stuff ### 
import setup_path
import airsim
import numpy as np
import os
import tempfile
import pprint
import cv2
import torch
import torch.nn.functional as F
import time
## Pizzairnet and stuff 
import sys
# Imports stuff from parent folders which is a little involved
## Receiving
sys.path.append('..')
from pizzairnet import PizzairNet,ResidualBlock,rgb2gray,add_noise
sys.path.pop(0)
# Imports stuff from parent folders which is a little involved
## Receiving
sys.path.append('../../flask_webapp/ReceivingData')
from jetson_to_dynamo import initialize_jetson_to_dynamo,insert_data
sys.path.pop(0)
## Sending
sys.path.append('../../flask_webapp/SendingData')
from dynamodb_to_jetson import fetch_from_dynamodb
sys.path.pop(0)

### need this stupid function to convert from quaternions to euler angles
def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = np.arctan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = np.arcsin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = np.arctan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z # in radians

###### Initialization Steps ######
print('Starting...')

### DynaDB Initialization ###
connect_to_db = False # Initializes DynaDB connection
if connect_to_db:
     dynamodb = initialize_jetson_to_dynamo()
# Grabs initial coordinate data from the DynaDB server. For now, just prints it out.
if connect_to_db:
    db_coordinates = fetch_from_dynamodb(dynamodb)
    print('Destination:',db_coordinates) # we won't use for AirSim demo - ill just hardcode some. 
db_last_upload_time = 0 # for less frequent uploading to DynaDB
upload_frequency = 10 # how many seconds should go by between coordinate uploads 
# some manually defined goals - one is at a warehouse one is outside a farm or some shit 
ware_goal_lat = 47.64153078517516
ware_goal_long = -122.14126947945815
farm_goal_lat =  47.64255048712882
farm_goal_long = -122.14138240085241
goal_tolerance = 2.920005174392924e-05
# sets the goal lat and long
goal_lat,goal_long = farm_goal_lat,farm_goal_long
#goal_lat,goal_long = ware_goal_lat,ware_goal_long

### ML initialization Initialization ### 
# various parameters and whatnot
max_speed = 5
do_control = True # Determines if actual drone commands are sent. Set to FALSE for code testing. 

# loads machine learning stuff
print('ML initializing...')
pizzair_model = torch.load('../models/model_v3.3.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()

### AirSim Initialization ###

# connect to the AirSim simulator
client = airsim.MultirotorClient() # the client is the object representing the drone
client.confirmConnection()
client.enableApiControl(True)

# notes on image APIS https://microsoft.github.io/AirSim/image_apis/#computer-vision-mode-1

# starts the drone at nice location
position = airsim.Vector3r(-45 , -4, 0)
heading = airsim.utils.to_quaternion(0, 0, -44.8)
pose = airsim.Pose(position, heading)
client.simSetVehiclePose(pose, True)

### Flight Begins Here ###

## takes off 3 m off the ground
#airsim.wait_key('Press any key to takeoff')
print("Taking off...")
client.armDisarm(True)
client.moveToZAsync(-5, 5).join()
client.takeoffAsync().join()
start_time = time.time()
## begins flight loop
continue_flight = True
command_interval = 1/10
flight_time = 10
with torch.no_grad():
    # stuff to handle showing framerate
    frame_counter = 0
    fps = 0
    last_time = time.time()
    hover = True
    while(continue_flight):
        ### Grabs image from AirSim client 
        responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = responses[0]
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
        img_rgb = img1d.reshape(response.height, response.width, 3)# reshape array to 4 channel image array H X W X 4
        frame = cv2.resize(img_rgb,(384,216))
        
        ### Machine Learning Inference Section ###
        frame = torch.tensor(frame).to(torch.float32).to(device).unsqueeze(0) # certified pytorch moment
        frame = rgb2gray(frame).unsqueeze(0)
        Y_train_hat = pizzair_model(frame)# runs through model
        frame_bw = np.squeeze(frame.cpu().numpy())
        cv2.imshow('frame', frame_bw) # Shows model input - frame in black and white
        mag = abs(Y_train_hat[0].item())*5 # seems to be systemic magnitude underprediction - manually fixing this for now 
        dir = np.argmax([Y_train_hat[1].tolist()[0][0],Y_train_hat[1].tolist()[0][2]])
        safe = np.argmax(Y_train_hat[2].tolist()[0])
        #safe = F.softmax(torch.tensor(Y_train_hat[2].tolist()[0]))
        print_string = ''

        ### Display Output Section ###
        dir_print = ''
        if dir == 0:
            dir_print = 'L'
        elif dir == 1:
            dir_print = 'R'
        else:
            dir_print = 'R'
        # adds network output
        print_string += ('Mag: ' + str(round(mag,5)) + ' Direction: '+ str(dir_print) + ' safe: ' + str(safe))
        # adds operation speed
        print_string += (' | FPS: ' + str(fps))
        print(print_string, end='\r')
        # time stuff
        if (time.time()-last_time) >= 1.0:
            fps = frame_counter
            frame_counter = 0
            last_time = time.time()
        else:
            #print(time.time()-last_time)
            frame_counter += 1
        ### Drone Control Section ###
        safe = np.argmax(Y_train_hat[2].tolist()[0])
        if do_control:
            if not hover:
                # this inner section is where the real control is going on
                if safe==0:
                    # safe - go forward
                    client.moveByVelocityBodyFrameAsync(vx=max_speed,vy=0,vz=0,duration=command_interval).join()
                    # gets angle between x-axis and goal assuming drone is at origin
                    gps_data = client.getGpsData()
                    lat = gps_data.gnss.geo_point.latitude
                    long = gps_data.gnss.geo_point.longitude
                    goal_angle = np.arctan2((goal_long-long),(goal_lat-lat)) # this should be in radians


                else:
                    # unsafe - go half speed, avoid things
                    if dir == 1: # go right
                        client.rotateByYawRateAsync(yaw_rate=mag*90,duration=command_interval).join()
                        client.moveByVelocityBodyFrameAsync(vx=max_speed/2,vy=0,vz=0,duration=command_interval).join()
                    elif dir == 0: # go left
                        client.rotateByYawRateAsync(yaw_rate=-mag*90,duration=command_interval).join()
                        client.moveByVelocityBodyFrameAsync(vx=max_speed/2,vy=0,vz=0,duration=command_interval).join()
                    else: # go straight
                        client.moveByVelocityBodyFrameAsync(vx=max_speed/2,vy=0,vz=0,duration=command_interval).join()
            else:
                client.moveByVelocityBodyFrameAsync(vx=0,vy=0,vz=0,duration=command_interval).join()

        ### DynaDB Data Uploading ###
        ## grabs relevant info from AirSim specific things
        if connect_to_db and abs(time.time()-db_last_upload_time) >= upload_frequency:
            imu_data = client.getImuData()
            gps_data = client.getGpsData()
            latitude = str(gps_data.gnss.geo_point.latitude)
            longitude = str(gps_data.gnss.geo_point.longitude)
            accel_x = str(imu_data.linear_acceleration.x_val)
            accel_y = str(imu_data.linear_acceleration.y_val)
            accel_z = str(imu_data.linear_acceleration.z_val)
            db_last_upload_time = time.time()
            image_url = 'https://cdn.mos.cms.futurecdn.net/76XArwuAqGZUGwffH2inpf-970-80.jpg'
            gps_coordinates = {'latitude': {'N': latitude}, 'longitude': {'N': longitude}}
            accelerometer_info = {'x': {'N': accel_x}, 'y': {'N': accel_y}, 'z': {'N': accel_z}}
            control_info = {'mag': str(mag), 'direction': str(dir_print),'Safety': str(safe)}
            insert_data(dynamodb,image_url, gps_coordinates, accelerometer_info, control_info) 
        #if abs(time.time()-db_last_upload_time) >= 10:
        #    db_last_upload_time = time.time()
        #print(time.time()-db_last_upload_time)
        ## uploads to dynadb

        

        ### Safety/Loop Exiting Section ###
        # desired button of your choice 
        pressedKey = cv2.waitKey(1) & 0xFF
        if pressedKey == ord('q'):
            break
        elif pressedKey == ord('h'):
            hover = not hover
        
## ends flight. lands.
print('Landing ... ')
client.landAsync(timeout_sec=0.5).join()

# end of flight. disables program.
client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)

