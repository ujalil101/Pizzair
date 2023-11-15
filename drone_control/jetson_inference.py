
# import the opencv library 
import cv2 
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
from pizzairnet import PizzairNet, ResidualBlock
def rgb2gray(rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,:,0], rgb[:,:,:,1], rgb[:,:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray/256.0
  
# define a video capture object 
vid = cv2.VideoCapture(0) 
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# loads machine learning stuff
pizzair_model = torch.load('models/pizzairnet_v1_checkpoint_24.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()
with torch.inference_mode():
    while(True): 
        
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

        print('Mag: ' + str(mag) + ' Direction: '+ str(np.argmax(dir)-1) + ' safe: ' + str(np.argmax(safe)), end='\r')

        # the 'q' button is set as the 
        # quitting button you may use any 
        # desired button of your choice 
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
    
    # After the loop release the cap object 
    vid.release() 
    # Destroy all the windows 
    cv2.destroyAllWindows() 