from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
import pickle
import numpy as np
import random

class PizzairNet(nn.Module):
    """
    Right now this is just a shallow ResNet architecture 

    """
    def __init__(self, block, layers):
        super(PizzairNet, self).__init__()
        self.inplanes = 64
        self.conv1 = nn.Sequential(
                        nn.Conv2d(1, 64, kernel_size = 7, stride = 2, padding = 3),
                        nn.BatchNorm2d(64),
                        nn.ReLU())
        self.maxpool = nn.MaxPool2d(kernel_size = 3, stride = 2, padding = 1)
        self.layer0 = self._make_layer(block, 64, layers[0], stride = 1)
        self.layer1 = self._make_layer(block, 128, layers[1], stride = 2)
        self.layer2 = self._make_layer(block, 256, layers[2], stride = 2)
        self.layer3 = self._make_layer(block, 512, layers[3], stride = 2)
        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc1 = nn.Linear(3072, 1024)
        self.fc_mag = nn.Linear(1024, 1) # single steering magnitude
        self.fc_dir = nn.Linear(1024, 3) # left, center, right
        self.fc_safety = nn.Linear(1024, 2) # safe, dangerous
        self.activation = nn.ReLU()
        
    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes:
            
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes, kernel_size=1, stride=stride),
                nn.BatchNorm2d(planes),
            )
        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)
    
    
    def forward(self, x):
        # conv layers
        x = self.conv1(x)
        x = self.maxpool(x)
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        # first bit of not conv stuff
        x = self.avgpool(x)
        x = self.activation(x.view(x.size(0), -1))
        x = self.activation(self.fc1(x))

        # output layers
        mag = self.fc_mag(x)
        direc = self.fc_dir(x)
        safe = self.fc_safety(x)

        return [mag,direc,safe]
    def loss(self,y_pred,y_true,epoch,regression_warmup=True):
        # weighting parameters - gotta tune these manually
        alpha_mag = 1
        alpha_dir = 1
        alpha_safe = 1

        # defines some loss functions
        mse = torch.nn.MSELoss()
        mag_ce = torch.nn.CrossEntropyLoss()
        safe_ce = torch.nn.CrossEntropyLoss()

        # unpacks our things
        mag_pred,dir_pred,safe_pred = y_pred[0],y_pred[1],y_pred[2]
        mag_true,dir_true,safe_true = y_true[:,0].unsqueeze(1),y_true[:,1].to(torch.int64),y_true[:,2].to(torch.int64)

        # MSE loss for magnitude
        mag_loss = mse(mag_pred,mag_true)

        # CE loss for direction
        dir_loss = mag_ce(dir_pred,dir_true)

        # BCE loss for safety
        safe_loss = safe_ce(safe_pred,safe_true)

        # adds and weights accordingly, including epsilon thing
        decay = 1/10
        epoch_null = 10
        ce_loss_multiplier = 1
        if regression_warmup:
            ce_loss_multiplier = max(0,(1-np.exp(-decay*(epoch-epoch_null))))
        loss = (alpha_mag * mag_loss) + ce_loss_multiplier * ((alpha_dir * dir_loss) + (alpha_safe * safe_loss))
        return loss
    
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride = 1, downsample = None):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Sequential(
                        nn.Conv2d(in_channels, out_channels, kernel_size = 3, stride = stride, padding = 1),
                        nn.BatchNorm2d(out_channels),
                        nn.ReLU())
        self.conv2 = nn.Sequential(
                        nn.Conv2d(out_channels, out_channels, kernel_size = 3, stride = 1, padding = 1),
                        nn.BatchNorm2d(out_channels))
        self.downsample = downsample
        self.relu = nn.ReLU()
        self.out_channels = out_channels
        
    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.conv2(out)
        if self.downsample:
            residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out