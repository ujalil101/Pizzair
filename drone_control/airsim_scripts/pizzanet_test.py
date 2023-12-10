import setup_path
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2
import torch
import time
def rgb2gray_airsim(rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,:,0], rgb[:,:,:,1], rgb[:,:,:,2]
        mult_factor = 0.91
        r_weight = 0.2989*mult_factor
        g_weight = 0.5870*mult_factor
        b_weight = 0.1140*mult_factor
        gray = r_weight * r + g_weight * g + b_weight * b
        return gray
print('Starting...')
# various parameters and whatnot
max_speed = 2
do_control = True # Determins if actual drone commands are sent. Set to FALSE for code testing. 

# loads machine learning stuff
print('ML initializing...')
pizzair_model = torch.load('../models/pizzairnet_v1_checkpoint_100.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()

### Flight Begins Here ###
# connect to the AirSim simulator
client = airsim.MultirotorClient() # the client is the object representing the drone
client.confirmConnection()
client.enableApiControl(True)

# notes on image APIS https://microsoft.github.io/AirSim/image_apis/#computer-vision-mode-1

# starts the drone at nice location
position = airsim.Vector3r(-45 , -4, 0)
heading = airsim.utils.to_quaternion(0, 0, -45)
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
        responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        response = responses[0]
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 
        # reshape array to 4 channel image array H X W X 4
        img_rgb = img1d.reshape(response.height, response.width, 3)
        # original image is fliped vertically
        #img_rgb = np.flipud(img_rgb)
        frame = cv2.resize(img_rgb,(384,216))
        # Display the resulting frame 
        cv2.imshow('frame', frame) 
        
        ### Machine Learning Inference Section ###
        # runs through model
        frame = torch.tensor(frame).to(torch.float32).to(device).unsqueeze(0) # certified pytorch moment
        frame = rgb2gray_airsim(frame).unsqueeze(0)
        #print(frame.shape)
        Y_train_hat = pizzair_model(frame)
        #print("\r", end="")
        mag = abs(Y_train_hat[0].item())
        dir = np.argmax([Y_train_hat[1].tolist()[0][0],Y_train_hat[1].tolist()[0][2]])
        safe = np.argmax(Y_train_hat[2].tolist()[0])
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
        if do_control:
            if not hover:
                if safe==0:
                    # safe - go forward
                    client.moveByVelocityBodyFrameAsync(vx=max_speed,vy=0,vz=0,duration=command_interval).join()
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
        ### Safety/Loop Exiting Section ###
        # desired button of your choice 
        pressedKey = cv2.waitKey(1) & 0xFF
        if pressedKey == ord('q'):
            break
        elif pressedKey == ord('h'):
            hover = not hover
        
## ends flight. lands.
print('Landing ... ')
client.landAsync(timeout_sec=5).join()

# end of flight. disables program.
client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)

