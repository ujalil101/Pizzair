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

# connect to the AirSim simulator
client = airsim.MultirotorClient() # the client is the object representing the drone
client.confirmConnection()
client.enableApiControl(True)

#position = airsim.Vector3r(-100 , -100, 1)
#heading = airsim.utils.to_quaternion(0, 0, 0)
#pose = airsim.Pose(position, heading)
#client.simSetVehiclePose(pose, True)
time.sleep(1)
# notes on image APIS https://microsoft.github.io/AirSim/image_apis/#computer-vision-mode-1
imu_data = client.getImuData()
gps_data = client.getGpsData()
latitude = str(gps_data.gnss.geo_point.latitude)
longitude = str(gps_data.gnss.geo_point.longitude)
ori = imu_data.orientation
_,_,yaw = euler_from_quaternion(ori.x_val,ori.y_val,ori.z_val,ori.w_val)
#euler_from_quaternion
print('Latitude:',latitude,'|| Longitude:',longitude,'|| Yaw:',yaw)
## ends flight. lands.
print('Landing ... ')
client.landAsync(timeout_sec=0.5).join()

# end of flight. disables program.
time.sleep(1)
client.reset()
client.armDisarm(False)

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)

