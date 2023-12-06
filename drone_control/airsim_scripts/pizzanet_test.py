import setup_path
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2
import torch

# ML preconditioning - loads network 

pizzair_model = torch.load('../models/pizzairnet_v1_checkpoint_100.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()
# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

