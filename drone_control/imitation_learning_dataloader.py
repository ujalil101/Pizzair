from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import numpy as np
import imageio
import decord
import torch
import math
from decord import VideoLoader
from decord import cpu, gpu

class ImitationDataLoader():
    # Imitation learning data loader. Basically just a wrapper for
    # the decoder video loader that also handles label loading. 
    # see https://github.com/dmlc/decord
    def __init__(self,
                 video_name_list, 
                 batch_size = 64, 
                 video_directory = '../../data/sim_video_clips/',
                 label_directory = '../../data/sim_labels/',
                 #video_size = (720,1280)):
                 video_size = (216,384)):
        decord.bridge.set_bridge('torch')
        video_files = []
        for name in video_name_list:
            video_files.append(video_directory + 'vid_' + name + '.mp4')
        self.vl = VideoLoader(video_files, ctx=[cpu(0)], shape=(batch_size,video_size[0],video_size[1],3), interval=0, skip=0, shuffle=1)
        self.batch_size = batch_size
        self.video_size = video_size
        # notes on shuffling above - 
        """
        shuffle = -1  # smart shuffle mode, based on video properties, (not implemented yet)
        shuffle = 0  # all sequential, no seeking, following initial filename order
        shuffle = 1  # random filename order, no random access for each video, very efficient
        shuffle = 2  # random order
        shuffle = 3  # random frame access in each video only """
        # handles safety labels
        safety_labels = []
        for video_file in video_name_list:
            safety_temp = np.load(label_directory + 'label_safety_'+video_file+'.npy')
            safety_labels.append(safety_temp.tolist())
        self.safety_labels = safety_labels

        # handles steering labels
        steering_labels = []
        for video_file in video_name_list:
            steer_temp = np.load(label_directory + 'label_steering_'+video_file+'.npy')
            steering_labels.append(steer_temp.tolist())
        self.steering_labels = steering_labels
    def __len__(self):
        return self.vl.__len__()
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            video_batch, indices = self.vl.__next__()
            mag_batch = []
            dir_batch = []
            safety_batch = []
            for index in indices:
                mag_batch.append(abs(self.steering_labels[index[0]][index[1]]))
                dir_batch.append(np.sign(self.steering_labels[index[0]][index[1]])+1)
                safety_batch.append(self.safety_labels[index[0]][index[1]])
            # converts video to greyscale
            video_batch = self.rgb2gray(video_batch)
            # puts the steering/safety stuff into right tensor size
            labels = torch.zeros((self.batch_size,3))
            labels[:,0] = torch.tensor(mag_batch)
            labels[:,1] = torch.tensor(dir_batch)
            labels[:,2] = torch.tensor(safety_batch)
            video_batch = torch.reshape(video_batch,(self.batch_size,1,self.video_size[0],self.video_size[1]))
            return video_batch,labels
        except:
            raise StopIteration
    def rgb2gray(self,rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,:,0], rgb[:,:,:,1], rgb[:,:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray

# note - this should not be used. it is inefficent, just kept for posterity 
class ImitationDatasetOld(Dataset):

    def __init__(self,video_name_list, video_directory = '../../data/sim_video_clips/',label_directory = '../../data/sim_labels/'):
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
        index_tuple = self.sample_to_video[idx]
        vid_file_index, frame_index = index_tuple[0],index_tuple[1]
        frame = self.video_object_list[vid_file_index].get_data(frame_index)
        #print(frame.shape)
        frame = self.rgb2gray(frame)
        # converts into (steer_mag,steer_dir,safety) - that's regression, 3 classes, boolean 
        steer = self.steering_labels[idx]
        safety = self.safety_labels[idx]
        return frame, steer, safety
    
    def rgb2gray(self,rgb):
        # little helper function for greyscale conversion
        r, g, b = rgb[:,:,:,0], rgb[:,:,:,1], rgb[:,:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray/256.0