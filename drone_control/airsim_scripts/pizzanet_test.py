import setup_path
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2
import torch
import time


# ML preconditioning - loads network 

pizzair_model = torch.load('../models/pizzairnet_v1_checkpoint_100.pth')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
pizzair_model.to(device)
pizzair_model.eval()
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
# flight starts here
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
while(continue_flight):
    #client.moveByRollPitchYawThrottleAsync(roll=0,pitch=-.1,yaw=1.0,duration=10,throttle=1).join()
    #client.moveByVelocityZAsync(10,10,10,0.1).join()
    #client.moveToZAsync(z=200,velocity=200000).join()
    client.rotateByYawRateAsync(yaw_rate=(np.random.random()-0.5)*90,duration=command_interval).join()
    client.moveByVelocityBodyFrameAsync(vx=5,vy=0,vz=0,duration=command_interval).join()
    desired_velocity = 10
    altitude = 3

    #vx, vy, _ = transformToEarthFrame([desired_velocity, 0, 0], client.getImuData().orientation)
    #client.moveByVelocityZBodyFrameAsync(vx=5, vy=5, z=altitude, duration=command_interval).join()
    #client.rotateByYawRateAsync(yaw_rate=45,duration=command_interval)
    #time.sleep(command_interval)
    if time.time()-start_time>flight_time:
        continue_flight = False
    #print(client.getGpsData().gnss.geo_point.altitude)
## ends flight. lands.
print('Landing ... ')
client.landAsync(timeout_sec=5).join()

# end of flight. disables program.
client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)

