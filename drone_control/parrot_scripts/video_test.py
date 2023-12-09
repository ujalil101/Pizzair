import cv2
from pyardrone import ARDrone

cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 384)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 216)
drone = ARDrone()
running = True
while running:
    # get current frame of video
    running, frame = cam.read()
    if running:
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            # escape key pressed
            running = False
    else:
        # error reading frame
        print ('error reading video feed')
cam.release()
cv2.destroyAllWindows()