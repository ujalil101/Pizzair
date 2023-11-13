from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import numpy as np
import imageio

class ImitationDataset(Dataset):

    def __init__(self, video_directory,label_directory,video_name_list):
        # saves arguments as local variables. not sure we actually 
        # need them again but can't hurt
        self.video_dir = video_directory
        self.label_dir = label_directory
        self.video_name_list = video_name_list

        # Needed structures to fill out 
        safety_labels = []
        steering_labels = []
        video_object_list = []
        sample_to_video = [] # sample of index i gives tuple of (vid_file_index, frame_index)

        # handles video files 
        for j,video_file in enumerate(video_name_list):
            vid = imageio.get_reader(video_directory + 'vid_'+video_file+'.mp4','ffmpeg')
            video_object_list.append(vid)
            k = 0
            for frame in vid:
                sample_to_video.append((j,k))
                k += 1
        self.video_object_list = video_object_list
        self.sample_to_video = sample_to_video
        
        # handles safety labels
        for video_file in video_name_list:
            safety_temp = np.load(label_directory + 'label_safety_'+video_file+'.npy')
            safety_labels = np.concatenate((safety_labels,safety_temp))
        self.safety_labels = safety_labels

        # handles steering labels
        for video_file in video_name_list:
            steer_temp = np.load(label_directory + 'label_steering_'+video_file+'.npy')
            steering_labels = np.concatenate((steering_labels,steer_temp))
        self.steering_labels = steering_labels

    def __len__(self):
        return len(self.safety_labels)

    # return a pair x,y at the index idx in the data set
    def __getitem__(self, idx):
        vid_file_index, frame_index = self.sample_to_video(idx)
        frame = self.video_object_list[vid_file_index]
        frame = self.rgb2gray(frame)
        steer = self.steering_labels[idx]
        safety = self.safety_labels[idx]
        return frame, steer, safety
    
    def rgb2gray(rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray