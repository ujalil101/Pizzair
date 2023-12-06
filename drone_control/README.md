# Pizzair - Drone Control Information

## Control Overview
Pizzair is powered by a combination of classical control algorithms for drone flight with an imitation-learning based algorithm for obstacle detection and avoidance. It is closest to the [Learning to Fly by Driving](https://ieeexplore.ieee.org/abstract/document/8264734) paper (from now on, the "DroNet Paper"). 

## Network Description
Pizzair's obstacle avoidance is a deep convolutional neural network (CNN) trained using imitation learning. It takes in a monocular camera image from the drone as input, and outputs a safety label, steering direction, and steering magnitude. The safety label is identical to the DroNet paper. 

We decouple steering direction (left, right, forward) from the magnitude because the steering in our training data is explicitly to avoid obstacles and /emph{not} to path-follow like DroNet. This training direction via regression a bad model - if you imagine avoiding a lamppost you are approaching head-on, the steering expert policy distribution should be bimodal between a hard left and hard right bank, but if our training data has an equal amount of left and right "dodges" in the training dataset, it will learn the emperical mean and fly into the obstacle. Decoupling essentially lets the network learn a very crude parametricization of that bimodal expert distribution - in the same scenario where left and right dodges are equally likely, it will learn a high probability of flying left or right with a high magnitude, both of which are safe. 

For some motivation for our approach, imitation learning combines the upsides of machine-learning based approaches compared to a modular pipeline (lack of required engineer fine-tuning, generalizability, the ability to connect perception to control via end-to-end learning) but without the downsides of a reinforcement learning approach (high samle complexity, training instability).

## Training Description
Pizzair is primarily trained with data from high visual-fidelity open-world videogames. Video games offer some advantages and disadvatages compared to colleting data from the real-world or in dedicated robot learning simulators (for instance, CARLA or AirSim). The advantages are a near-photorealism and stellar environment diversity. For example, Watch Dogs 2 looks nearly photorealistic and contains a scaled-down version of Northern California, including San Francisco and its many districts, suburbs in the Bay Area, and forested park environments. In comparision, CARLA has only a limited selection of small, homogenous maps and poor fidelity. The downsides are that video games are less flexible for researchers and have less realistic physics simulations. 


Specifically, I collected around 30,000 image samples by flying around various environments in Watch Dogs 2, [INSERT OTHER GAMES]