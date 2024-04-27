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
import matplotlib.image
## Pizzairnet and stuff 
import sys
# Imports stuff from parent folders which is a little involved
## Receiving
sys.path.append('..')
from pizzairnet import PizzairNet,ResidualBlock,rgb2gray,add_noise,flip_image
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

def check_reached_destination(client):
    gps_data = client.getGpsData()
    latitude = gps_data.gnss.geo_point.latitude
    longitude = gps_data.gnss.geo_point.longitude
    if np.sqrt((goal_lat-latitude)**2 + (goal_long-longitude)**2) <= goal_tolerance:
        return True
    return False

def control_drone_step_discrete_old(client,dir,mag,safe,safety_threshold,hover):
    safe = F.softmax(safe,dim=0)[1] > safety_threshold
    if do_control:
        if not hover:
            # this inner section is where the real control is going on
            if safe==0:
                # safe - go forward
                if not do_navigation:
                    client.moveByVelocityBodyFrameAsync(vx=max_speed,vy=0,vz=0,duration=command_interval_safe).join()
                else:
                    # gets angle between x-axis and goal assuming drone is at origin
                    gps_data = client.getGpsData()
                    lat = gps_data.gnss.geo_point.latitude
                    long = gps_data.gnss.geo_point.longitude
                    goal_angle = np.arctan2((goal_long-long),(goal_lat-lat))% ((2)*np.pi) # this should be in radians
                    # WARNING: war crime gets commmitted in next couple lines
                    imu_data = client.getImuData()
                    ori = imu_data.orientation
                    _,_,yaw = euler_from_quaternion(ori.x_val,ori.y_val,ori.z_val,ori.w_val)
                    ego_angle = (yaw % ((2)*np.pi)) # converts "airsim radians" to "normal people radians"
                    angle_diff = (goal_angle-ego_angle) % ((2)*np.pi)
                    #print('Angle Diff:',angle_diff)
                    if angle_diff < np.pi: # go left
                        dir = 1
                    else: # go right
                        angle_diff = (-angle_diff) % ((2)*np.pi) # makes upcoming thing agonstic which is nice
                        dir = -1
                    if angle_diff < np.pi/2: # in 180-FOV "cone": turn proportional to mag
                        mag = angle_diff/(np.pi/2)
                    else: # outside FOV cone/"behind" drone - turn as fast as possible, which we use normalized 1 for
                        mag = 1
                    client.rotateByYawRateAsync(yaw_rate=mag*dir*90,duration=command_interval_safe).join()
                    client.moveByVelocityBodyFrameAsync(vx=max_speed,vy=0,vz=0,duration=command_interval_safe).join()

            else:
                # unsafe - go half speed, avoid things
                if dir == 1: # go right
                    client.rotateByYawRateAsync(yaw_rate=mag*90,duration=command_interval_danger).join()
                    client.moveByVelocityBodyFrameAsync(vx=max_speed*safety_speed_ratio,vy=0,vz=0,duration=command_interval_danger).join()
                elif dir == 0: # go left
                    client.rotateByYawRateAsync(yaw_rate=-mag*90,duration=command_interval_danger).join()
                    client.moveByVelocityBodyFrameAsync(vx=max_speed*safety_speed_ratio,vy=0,vz=0,duration=command_interval_danger).join()
                else: # go straight
                    client.moveByVelocityBodyFrameAsync(vx=max_speed*safety_speed_ratio,vy=0,vz=0,duration=command_interval_danger).join()
        else:
            client.moveByVelocityBodyFrameAsync(vx=0,vy=0,vz=0,duration=command_interval_danger).join()
    return client,dir,mag

def control_drone_step_test(client,dir,mag,safe,safety_threshold,hover):
    safe = F.softmax(safe,dim=0)[1] > safety_threshold
    #safe = 0
    drivetrain = airsim.DrivetrainType.ForwardOnly
    yaw_mode = airsim.YawMode(is_rate= False, yaw_or_rate = 0)
    if do_control:
        if not hover:
            # this inner section is where the real control is going on
            if safe==0:
                # safe - go forward
                if not do_navigation:
                    client.moveByVelocityBodyFrameAsync(vx=max_speed,vy=0,vz=0,duration=command_interval_safe).join()
                else:
                    # gets angle between x-axis and goal assuming drone is at origin
                    gps_data = client.getGpsData()
                    lat = gps_data.gnss.geo_point.latitude
                    long = gps_data.gnss.geo_point.longitude
                    goal_angle = np.arctan2((goal_long-long),(goal_lat-lat))% ((2)*np.pi) # this should be in radians
                    # WARNING: war crime gets commmitted in next couple lines
                    imu_data = client.getImuData()
                    ori = imu_data.orientation
                    _,_,yaw = euler_from_quaternion(ori.x_val,ori.y_val,ori.z_val,ori.w_val)
                    ego_angle = (yaw % ((2)*np.pi)) # converts "airsim radians" to "normal people radians"
                    angle_diff = (goal_angle-ego_angle) % ((2)*np.pi)
                    #print('Angle Diff:',angle_diff)
                    if angle_diff < np.pi: # go left
                        dir = 1
                    else: # go right
                        angle_diff = (-angle_diff) % ((2)*np.pi) # makes upcoming thing agonstic which is nice
                        dir = -1
                    if angle_diff < np.pi/2: # in 180-FOV "cone": turn proportional to mag
                        mag = angle_diff/(np.pi/2)
                    else: # outside FOV cone/"behind" drone - turn as fast as possible, which we use normalized 1 for
                        mag = 1
                    # to induce more aggressive goal-following
                    mag = mag * 2
                    client.moveByVelocityBodyFrameAsync(max_speed, mag*dir, 0, command_interval_safe, drivetrain=drivetrain,yaw_mode=yaw_mode).join()

            else:
                # unsafe - go half speed, avoid things
                mag = mag * 2
                if dir == 1: # go right
                    client.moveByVelocityBodyFrameAsync(max_speed*safety_speed_ratio, mag, 0, command_interval_safe, drivetrain=drivetrain,yaw_mode=yaw_mode).join()
                    #client.moveByVelocityBodyFrameAsync(vx, vy, 0, command_interval_safe, airsim.DrivetrainType.ForwardOnly).join()
                elif dir == 0: # go left
                    client.moveByVelocityBodyFrameAsync(max_speed*safety_speed_ratio, mag*-1, 0, command_interval_safe, drivetrain=drivetrain,yaw_mode=yaw_mode).join()
                else: # go straight
                    client.moveByVelocityBodyFrameAsync(max_speed*safety_speed_ratio, 0, 0, command_interval_safe, drivetrain=drivetrain,yaw_mode=yaw_mode).join()
        else:
            client.moveByVelocityBodyFrameAsync(vx=0,vy=0,vz=0,duration=command_interval_danger).join()
    return client,dir,mag

def control_drone_step_blind(client,dir,mag,safe,safety_threshold,hover):
    # this method ONLY blindly goes towards the goal, mostly for testing purposes
    drivetrain = airsim.DrivetrainType.ForwardOnly
    yaw_mode = airsim.YawMode(is_rate= False, yaw_or_rate = 0)
    if do_control:
        if not hover:
            gps_data = client.getGpsData()
            lat = gps_data.gnss.geo_point.latitude
            long = gps_data.gnss.geo_point.longitude
            goal_angle = np.arctan2((goal_long-long),(goal_lat-lat))% ((2)*np.pi) # this should be in radians
            # WARNING: war crime gets commmitted in next couple lines
            imu_data = client.getImuData()
            ori = imu_data.orientation
            _,_,yaw = euler_from_quaternion(ori.x_val,ori.y_val,ori.z_val,ori.w_val)
            ego_angle = (yaw % ((2)*np.pi)) # converts "airsim radians" to "normal people radians"
            angle_diff = (goal_angle-ego_angle) % ((2)*np.pi)
            #print('Angle Diff:',angle_diff)
            if angle_diff < np.pi: # go left
                dir = 1
            else: # go right
                angle_diff = (-angle_diff) % ((2)*np.pi) # makes upcoming thing agonstic which is nice
                dir = -1
            if angle_diff < np.pi/2: # in 180-FOV "cone": turn proportional to mag
                mag = angle_diff/(np.pi/2)
            else: # outside FOV cone/"behind" drone - turn as fast as possible, which we use normalized 1 for
                mag = 1
            #vx = np.cos(mag) * max_speed
            #vy = np.sin(mag) * max_speed
            vx = 0
            vy = 1
            client.moveByVelocityBodyFrameAsync(vx, vy, 0, command_interval_safe, drivetrain=drivetrain,yaw_mode=yaw_mode).join()
    return client,dir,mag

def print_control_commands(dir,mag,safe,frame_counter,last_time,fps):
    safe = F.softmax(safe,dim=0)
    print_string = ''
    dir_print = ''
    if dir == 0:
        dir_print = 'L'
    elif dir == 1:
        dir_print = 'R'
    else:
        dir_print = 'C'
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
    return frame_counter,last_time,fps,dir_print

def get_airsim_image(client):
    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
    response = responses[0]
    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
    img_rgb = img1d.reshape(response.height, response.width, 3)# reshape array to 4 channel image array H X W X 4
    frame = cv2.resize(img_rgb,(384,216))
    return frame

def get_model_predictions(frame,device,pizzair_model):
    frame = torch.tensor(frame).to(torch.float32).to(device).unsqueeze(0) # certified pytorch moment
    frame = rgb2gray(frame).unsqueeze(0)
    #frame = add_noise(frame,device)
    #frame = flip_image(frame,device)
    Y_train_hat = pizzair_model(frame)# runs through model
    frame_bw = np.squeeze(frame.cpu().numpy())
    cv2.imshow('frame', frame_bw) # Shows model input - frame in black and white
    mag = abs(Y_train_hat[0].item())*5 # seems to be systemic magnitude underprediction - manually fixing this for now 
    #mag = abs(Y_train_hat[0].item())
    dir = np.argmax([Y_train_hat[1].tolist()[0][0],Y_train_hat[1].tolist()[0][2]])
    #print(Y_train_hat[1])
    safe = torch.tensor(Y_train_hat[2].tolist()[0])
    return mag,dir,safe

def dynadb_upload(connect_to_db,db_last_upload_time,upload_frequency,client):
    if connect_to_db and abs(time.time()-db_last_upload_time) >= upload_frequency:
        imu_data = client.getImuData()
        gps_data = client.getGpsData()
        latitude = str(gps_data.gnss.geo_point.latitude)
        longitude = str(gps_data.gnss.geo_point.longitude)
        accel_x = str(imu_data.linear_acceleration.x_val)
        accel_y = str(imu_data.linear_acceleration.y_val)
        accel_z = str(imu_data.linear_acceleration.z_val)
        db_last_upload_time = time.time()
        #image_url = 'https://cdn.mos.cms.futurecdn.net/76XArwuAqGZUGwffH2inpf-970-80.jpg'
        #image_url = 'https://drive.google.com/file/d/1-As1zn2TsJuEK84MXywNl-4OoShgc1zt/preview'
        #image_url = 'https://drive.usercontent.google.com/download?id=1-As1zn2TsJuEK84MXywNl-4OoShgc1zt'
        image_url = 'https://lh3.googleusercontent.com/d/1-As1zn2TsJuEK84MXywNl-4OoShgc1zt=s220?authuser=0'
        gps_coordinates = {'latitude': {'N': latitude}, 'longitude': {'N': longitude}}
        accelerometer_info = {'x': {'N': accel_x}, 'y': {'N': accel_y}, 'z': {'N': accel_z}}
        control_info = {'mag': str(mag), 'direction': str(dir_print),'Safety': str(safe)}
        insert_data(dynamodb,image_url, gps_coordinates, accelerometer_info, control_info) 
    return db_last_upload_time

def dynadb_download(connect_to_db):
    if connect_to_db:
        db_coordinates = fetch_from_dynamodb(dynamodb)
        #print('Destination:',db_coordinates) # we won't use for AirSim demo - ill just hardcode some. 
        return db_coordinates
    
    
###### Initialization Steps ######
print('Starting...')

### DynaDB Initialization ###
connect_to_db = False # Initializes DynaDB connection
if connect_to_db:
    dynamodb = initialize_jetson_to_dynamo()
db_last_upload_time = 0 # for less frequent uploading to DynaDB
upload_frequency = 5 # how many seconds should go by between coordinate uploads 

# Grabs initial coordinate data from the DynaDB server. For now, just prints it out.

db_coordinates = dynadb_download(connect_to_db)
#print(db_coordinates[0]['Deliver']['BOOL'])

# some manually defined goals - one is at a warehouse one is outside a farm or some shit 
ware_goal_lat = 47.64153078517516
ware_goal_long = -122.14126947945815
farm_goal_lat =  47.64255048712882
farm_goal_long = -122.14138240085241

test_goal_lat =  47.64167934164553
test_goal_long =  -122.14109613885682
goal_tolerance = 8e-05

# sets the goal lat and long
#goal_lat,goal_long = farm_goal_lat,farm_goal_long
goal_lat,goal_long = test_goal_lat,test_goal_long

### ML initialization Initialization ### 
# various parameters and whatnot
max_speed = 4
safety_speed_ratio = 1
do_control = True # Determines if actual drone commands are sent. Set to FALSE for code testing. 
do_navigation = True # Determins if the drone tries to reach a destination. Set ot FALSE for "wandering"
command_interval_safe = 1/5# How many seconds each command is told to happen
command_interval_danger = 1/5 # how many seconds unsafe/avoidance commands are told to happen
safety_threshold = 0.5

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

# grabs drone starting location
imu_data = client.getImuData()
gps_data = client.getGpsData()
start_lat = gps_data.gnss.geo_point.latitude
start_long = gps_data.gnss.geo_point.longitude

### Flight Begins Here ###

## takes off 3 m off the ground
#airsim.wait_key('Press any key to takeoff')
#print("Taking off...")
client.armDisarm(True)
start_time = time.time()
## begins flight loop
active = True # for if the overall awareness loop is active. 
#continue_flight = db_coordinates[0]['Deliver']['BOOL'] # if the drone should currently be flying. 
continue_flight = False #TODO change back for demo 
reached_destination = False
going_to_delivery = True
with torch.no_grad():
    # stuff to handle showing framerate
    frame_counter = 0
    fps = 0
    last_time = time.time()
    hover = False
    while(active):
        ### Grabs image from AirSim client 
        frame = get_airsim_image(client)
        cv2.imwrite('G:\My Drive/image.png',frame)
        ### Machine Learning Inference Section ###
        mag, dir, safe = get_model_predictions(frame,device,pizzair_model)

        ### Display Output Section ###
        frame_counter,last_time,fps,dir_print = print_control_commands(dir,mag,safe,frame_counter,last_time,fps)

        ### Section for Active Flight 
        if(continue_flight):
            ### Drone Control Section ###
            client,dir,mag = control_drone_step_test(client,dir,mag,safe,safety_threshold,hover)

            ### Checking if Destination is Reached ###
            reached_destination = check_reached_destination(client)

        ### Section for if drone is enabled, but server tells not to deliver. don't think anything really happens here 
        else:
            gg = 8+9
        
        ### Pre-defined set of things to do when we reach the goal. We land, change destination home <-> delivery, and continue!
        if(reached_destination):
            if going_to_delivery:
                print('Delivery destination reached. Delivering...')
                goal_lat,goal_long = start_lat,start_long
            else:
                print('Home destination reached. Landing...')
                goal_lat,goal_long = farm_goal_lat,farm_goal_long
            reached_destination = False
            going_to_delivery = not going_to_delivery
            time.sleep(3)
            client.moveToZAsync(3, 5).join()
            client.landAsync(timeout_sec=5).join()
            time.sleep(3)
            client.moveToZAsync(-5, 5).join()
            client.takeoffAsync().join()
            # flips destinations 
        
        ### DynaDB Command Downloading ###
        db_coordinates = dynadb_download(connect_to_db)
        if connect_to_db:
            new_command = db_coordinates[0]['Deliver']['BOOL']
        else:
            new_command = continue_flight

        ### Safety/Loop Exiting Section ###
        pressedKey = cv2.waitKey(1) & 0xFF
        if pressedKey == ord('q'): # Press Q to exit everything
            print('Flight terminated. Landing ... ')
            client.landAsync(timeout_sec=0.5).join()
            break
        elif pressedKey == ord('h'): # Press H to continue navigation, but hover in place
            hover = not hover
        elif pressedKey == ord('s'): # Press S to simulate DynaDB telling drone to stop flight
            new_command = not continue_flight

        ## Wasn't flying, now should - so takesoff!
        if new_command and not continue_flight:
            print("New Command: Deliver! \n")
            time.sleep(1)
            client.moveToZAsync(-5, 5).join()
            client.takeoffAsync().join()
        ## Was flying, now shouldn't - so land!
        elif not new_command and continue_flight:
            print('New Command: Land! \n')
            time.sleep(1)
            client.moveToZAsync(3, 5).join()
            client.landAsync(timeout_sec=5).join()
        continue_flight = new_command

        ### DynaDB Data Uploading ###
        db_last_upload_time = dynadb_upload(connect_to_db,db_last_upload_time,upload_frequency,client)

        

# end of flight. disables program.
client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)

