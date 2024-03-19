
### Imports 
import cv2 
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
import time
#from pizzairnet import PizzairNet, ResidualBlock
import sys
# Imports stuff from parent folders which is a little involved
## Receiving
sys.path.append('../../flask_webapp/ReceivingData')
from jetson_to_dynamo import initialize_jetson_to_dynamo,insert_data
sys.path.pop(0)
## Sending
sys.path.append('../../flask_webapp/SendingData')
from dynamodb_to_jetson import fetch_from_dynamodb
sys.path.pop(0)
## Pizzairnet and stuff 
sys.path.append('..')
from pizzairnet import PizzairNet,ResidualBlock,rgb2gray
sys.path.pop(0)

  
# Sets up OpenCV recording objects
vid = cv2.VideoCapture(0) 
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 384)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 216)

# Loads ML Model
pizzair_model = torch.load('../models/model_v3.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()

# Initializes DynaDB connection
#dynamodb = initialize_jetson_to_dynamo()

# Grabs initial coordinate data from the DynaDB server. For now, just prints it out.
#coordinates = fetch_from_dynamodb(dynamodb)
#print('Destination:',coordinates)

with torch.no_grad():
    frame_counter = 0
    fps = 0
    last_time = time.time()
    while(True): 
        #### ML/Control Loop ###

        # Capture the video frame 
        # by frame 
        ret, frame = vid.read() 

        frame = cv2.resize(frame,(384,216))
        # Display the resulting frame 
        cv2.imshow('frame', frame) 
        
        # runs through model
        frame = torch.tensor(frame).to(torch.float32).to(device).unsqueeze(0) # certified pytorch moment
        frame = rgb2gray(frame).unsqueeze(0)
        #print(frame.shape)
        Y_train_hat = pizzair_model(frame)
        #print("\r", end="")
        mag = Y_train_hat[0].item()
        dir = Y_train_hat[1].tolist()[0]
        safe = Y_train_hat[2].tolist()[0]
        print_string = ''
        # adds network output
        print_string += ('Mag: ' + str(mag) + ' Direction: '+ str(np.argmax(dir)-1) + ' safe: ' + str(np.argmax(safe)))
        # adds operation speed
        print_string += (' | FPS: ' + str(fps))
        print(print_string, end='\r')

        # time stuff
        if (time.time()-last_time) >= 1.0:
            fps = round(frame_counter,2)
            frame_counter = 0
            last_time = time.time()
        else:
            #print(time.time()-last_time)
            frame_counter += 1

        # the 'q' button is set as the 
        # quitting button you may use any 
        # desired button of your choice 
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

        #### DynaDB Data Uploading ###
        image_url = 'https://cdn.mos.cms.futurecdn.net/76XArwuAqGZUGwffH2inpf-970-80.jpg'
        gps_coordinates = {'latitude': {'N': '37.7749'}, 'longitude': {'N': '-122.4194'}}
        accelerometer_info = {'x': {'N': '0.5'}, 'y': {'N': '0.3'}, 'z': {'N': '0.7'}}
        control_info = {'mag': mag, 'direction': dir,'Safety': safe}
        #insert_data(dynamodb,image_url, gps_coordinates, accelerometer_info, control_info)
    
    # After the loop release the cap object 
    vid.release() 
    # Destroy all the windows 
    cv2.destroyAllWindows() 
