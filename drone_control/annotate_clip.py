import matplotlib.pyplot as plt
import numpy as np
# the following library makes this windows-specific - there is 
# probably a way to do it on Unix systems though. Sorry!
import msvcrt
import imageio
import os.path
import argparse

def convert_key_to_steer(key_list):
    steer_list = []
    # steering is -1 for far left, 1 for far right
    # converted from 1-9 range, excluding 5 - that is replaced by 
    # space to make recording easier. space is straight/0
    for key in key_list:
        new_key = 0.0
        if key == "b'1'":
            new_key = -1.0
        elif key == "b'2'":
            new_key = -0.75
        elif key == "b'3'":
            new_key = -0.5
        elif key == "b'4'":
            new_key = -0.25
        elif key == "b' '": # middle of range
            new_key = 0.0
        elif key == "b'6'":
            new_key = 0.25
        elif key == "b'7'":
            new_key = 0.5
        elif key == "b'8'":
            new_key = 0.75
        elif key == "b'9'":
            new_key = 1.0
        else:
            print('Warning: Invalid Steering Annotation: Replacing with Straight (0)')
        steer_list.append(new_key)
    return steer_list

def convert_key_to_safety(key_list):
    safety_list = []
    # s is "safe", d is "dagerous"
    for key in key_list:
        if key == "b's'":
            safety_list.append(0)
        elif key == "b'd'":
            safety_list.append(1)
        else:
            print('Warning: Invalid Safety Annotation: Replacing with Unsafe')
            safety_list.append(1)
    return safety_list

# Command line argument stuff'
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", help = "File name to read for annotation.")
parser.add_argument('-s', '--safety', action='store_true', help = "Enables safety annotations. Does steering by default.")  # on/off flag
parser.add_argument('-ld', '--load_dir', help = "Video file directory.")  
parser.add_argument('-sd', '--save_dir', help = "Save directory, for labelled annotations.")  

args = parser.parse_args()
# note - videos should be in format vid_[game]_[description].mp4
# if you forget the mp4, it will be added automatically. 
filename = args.filename
if filename.split('.')[-1] != '.mp4':
    filename = filename + '.mp4'
load_dir = '../../data/sim_video_clips/'
save_dir = '../../data/sim_labels/'
if args.load_dir: 
    load_dir = args.load_dir
if args.save_dir:
    save_dir = args.save_dir
if not args.filename:
    print('Error: No filename provided.')
    exit()
if not os.path.isfile(load_dir + filename):
    print('Error: File does not exist.')
    exit()

# Initializes viewing window
plt.ion()    
vid = imageio.get_reader(load_dir + filename,'ffmpeg')
key_list = []
for frame in vid:
    if 'ax' in globals(): ax.remove()
    ax = plt.imshow(frame)
    plt.pause(0.002) # I suspect this value could be machine-specific - try increasing it if you have problems
    key_press = str(msvcrt.getch())
    # checks for escape key - ends program if pressed
    if key_press == "b'\\x1b'": # the escape key 
        print('Exiting program')
        exit()

    key_list.append(key_press)
    
# Converts key presses to labels, depending on the given task
label_type = ''
if args.safety:
    key_list = convert_key_to_safety(key_list)
    label_type = 'safety'
else:
    key_list = convert_key_to_steer(key_list)
    label_type = 'steering'

# saves our labels
label_name = save_dir + 'label_' + label_type + '_' + ('_'.join(filename.split('_')[1:])).split('.')[0] + '.npy'
np.save(label_name,key_list)
print('Success: saved',len(key_list),'annotations')
plt.ioff()