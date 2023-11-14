from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
import pickle
import numpy as np
import random
from pizzairnet import PizzairNet, ResidualBlock
from imitation_learning_dataloader import ImitationDataLoader

# training configuration

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#pizzair_model = PizzairNet(ResidualBlock, [3, 4, 6, 3])


# data loading

video_list = ['wd2_brown',
              'wd2_city1',
              'wd2_city2',
              'wd2_office',
              'wd2_park1',
              'wd2_park2',
              'wd2_sub']
batch_size = 8

pizzair_model = PizzairNet(ResidualBlock, [2,2,2,2])
pizzair_model.to(device)
num_epochs = 2
optimizer = torch.optim.AdamW(pizzair_model.parameters(),lr=5e-4)

training_losses = np.zeros(num_epochs)

for epoch in range(num_epochs):
    # training
    pizzair_model.train()
    t_loss = 0.0
    t_num_correct = 0
    # need to "remake" it because it doens't reset as of now. oops 
    imitation_train_dataset = ImitationDataLoader(video_name_list=video_list[0:6],batch_size=batch_size)

    for X_train_batch,Y_train_batch in tqdm(imitation_train_dataset,desc='Epoch: '+str(epoch)):
        # puts on GPU
        X_train_batch = X_train_batch.to(device)
        Y_train_batch = Y_train_batch.to(device)
        
        optimizer.zero_grad()
        Y_train_hat = pizzair_model(X_train_batch)
        #print(Y_train_hat)
        #print(Y_train_batch)
        loss = pizzair_model.loss(Y_train_hat,Y_train_batch,epoch,regression_warmup=False)
        loss.backward()
        optimizer.step()
        t_loss += loss.item()

    training_losses[epoch]   = t_loss/(imitation_train_dataset.__len__()*batch_size)
    torch.save(pizzair_model,'models/pizzairnet_v1_1_no_reg_checkpoint_' + str(epoch) + '.pth')
    np.save('training_loss_recrd',training_losses)
