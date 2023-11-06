import matplotlib.pyplot as plt
import numpy as np
import msvcrt
import imageio

import argparse

def convert_key_to_steer(key_list):
    steer_list = []
    for key in key_list:
        #TODO convert
    return steer_list

def convert_key_to_safety(key_list):
    safety_list = []
    for key in key_list:
        #TODO convert
    return safety_list
# Command line argument stuff
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", help = "File name to read for annotation.")
parser.add_argument('-s', '--safety', action='store_true', help = "Enables safety annotations. Does steering by default.")  # on/off flag
parser.add_argument('-sd', '--save_dir', help = "Save directory.")  # on/off flag

args = parser.parse_args()
filename = args.filename
if not args.filename:
    print('Error: no filename provided.')
    exit()

# Grabs saving directory
save_directory = args.save_dir
if not args.save_dir:
    save_directory = 'sim_labels'

# Initializes viewing window
plt.ion()    
vid = imageio.get_reader(filename,'ffmpeg')
key_list = []
for frame in vid:
    if 'ax' in globals(): ax.remove()
    ax = plt.imshow(frame)
    plt.pause(0.01)
    thing = msvcrt.getch()
    plt.pause(0.01)
    key_list.append(thing)

# Converts key presses to labels, depending on the given task
if args.safety:
    np.save(save_directory + '/safety_' + convert_key_to_safety(key_list))
plt.ioff()