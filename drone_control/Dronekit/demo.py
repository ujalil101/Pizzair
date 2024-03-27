
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import argparse  

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='/dev/ttyUSB0:921600')

args = parser.parse_args()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % args.connect)
vehicle = connect(args.connect, baud=921600, wait_ready=True)
# 921600 is the baud rate that you have set in the mission planner or qgc

# Function to arm and then takeoff to a user-specified altitude
def arm_and_takeoff(aTargetAltitude):
    ready_to_arm = False

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    ready_to_arm = True
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Check that vehicle has reached takeoff altitude
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


ready_to_arm = False 

# NEED TO GET SIGNAL FROM THE SERVER TO TOGGLE THIS SO THE DRONE CAN START FLYING
# WHEN WE TELL IT TO. THIS IS A DEMO FOR NOW WE WILL BUILD ON TOP OF THIS
# FOR ADDRESS INPUT ETC ETC.




while True:
    if ready_to_arm:
        arm_and_takeoff(15)
        break 
    



# Initialize the takeoff sequence to 15m
arm_and_takeoff(15)

print("Take off complete")

# Hover for 10 seconds
time.sleep(15)

print("Now let's land")
vehicle.mode = VehicleMode("LAND")

# Close vehicle object
vehicle.close()
