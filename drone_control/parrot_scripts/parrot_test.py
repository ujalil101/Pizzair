import numpy as np
import cv2
import time
import torch
import matplotlib.pyplot as plt
from pyardrone import ARDrone
from pizzairnet import PizzairNet, ResidualBlock
# Note - PyARDrone API here
# https://pyardrone.readthedocs.io/en/latest/ardrone/#video-support

def rgb2gray(rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,:,0], rgb[:,:,:,1], rgb[:,:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray/256
print('Starting...')
# various parameters and whatnot
max_speed = 0.1
do_control = True # Determins if actual drone commands are sent. Set to FALSE for code testing. 

# sets up video recording stuff
print('Video initializing...')
vid = cv2.VideoCapture('tcp://192.168.1.1:5555')
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 384)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 216)
ret, frame = vid.read()

# sets up drone 
print('Drone initializing...')
drone = ARDrone()
drone.navdata_ready.wait()  # wait until NavData is ready

# loads machine learning stuff
print('ML initializing...')
pizzair_model = torch.load('../models/model_v2_all_ft.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()

### Flight Begins Here ###

# takes off 
if do_control:
    while not drone.state.fly_mask:
        drone.takeoff()
# main drone flying loop
with torch.no_grad():
    # stuff to handle showing framerate
    frame_counter = 0
    fps = 0
    last_time = time.time()
    hover = True
    while(True): 
            # Capture the video frame 
            ret, frame = vid.read() 
            if frame is None:
                break
            frame = cv2.resize(frame,(384,216))
            # Display the resulting frame 
            cv2.imshow('frame', frame) 
            
            ### Machine Learning Inference Section ###
            # runs through model
            frame = torch.tensor(frame).to(torch.float32).to(device).unsqueeze(0) # certified pytorch moment
            frame = rgb2gray(frame).unsqueeze(0)
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
                    if safe == 0:
                        # safe - go forward
                        drone.move(forward=max_speed)
                    else:
                        # unsafe - go half speed, avoid things
                        if dir == 1: # go right
                            drone.move(forward=0,cw=mag)
                        elif dir == 0: # go left
                            drone.move(forward=0,ccw=mag)
                        else: # go straight
                            drone.move(forward=max_speed/2)
                else:
                    drone.hover()
            ### Safety/Loop Exiting Section ###
            # desired button of your choice 
            pressedKey = cv2.waitKey(1) & 0xFF
            if pressedKey == ord('q'):
                break
            elif pressedKey == ord('h'):
                hover = not hover

### Flight Loop Over - Attempts Landing ###
print('Landing... ')
if do_control:
    while drone.state.fly_mask:
        drone.land()
