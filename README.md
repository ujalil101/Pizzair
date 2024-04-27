# Pizzair - Pizza Delivery Drone App

## Note for Senior Design Staff

Instead of one software Readme, we split it up into two readmes - one for the drone control software, and one for the web application. We put them as README.mds under the "drone_control" and "flask_webapp" folders respectively. The HW Readme is in the HW folder. 

## Project Overview
Pizzair is a cutting-edge pizza delivery system that uses drones to deliver pizzas to customers. This repository contains the code for the Pizzair mobile app, which allows customers to place orders and communicate with the pizza delivery drones.

<img width="578" alt="Screenshot 2023-10-08 at 3 07 45 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/8a8fca2d-9420-47b6-9bf8-23bf93679acf">

## Autonomous Drone Architecture 
![Image](https://github.com/ujalil101/Pizzair/assets/74789609/dd59714c-2825-41f7-a4df-d8da71cb4777)

## Getting Started/Engineering Addendum
Pizzair consists of three seperate components: the software that controls the drone, the software that runs the web application, and the physical drone platform hardware. The Pizzair platform is the combination of the two, and the two connect, but the two can also be run/used independently. 

For more details you can look at the specific README for each section in their appropriate folder, but as a broad overview:

Our Drone Control system is based on an imitation learning framework, that controls the drone using monocular camera vision for obstacle avoidance, and GPS/compass information for destination navigation. Our software is capable of running the full drone control system in the AirSim simulator, including integration with the web app. This is in a relatively complete state - it can navigate maybe like, 80-90% safely. Our current network is very right-dodge biased - I think a better training scheme could probably fix this. We didn't get to test this in the real world a ton - that would be an important place for future groups to expand on this. Finding a drone that has a simple controller (the thing that turns high-level commands like yaw steering or velocity into motor control), has a camera, and is cheap is surprisingly hard - the Parrot series of drones come close but have very limited software support. 

Our web application is a Flask webapp that stores a databse on AWS. This is also in a relatively complete state - there is some work to be done cleaning up the interface, but the basic structure is there. No gotchas. 

Our physical drone is the place where the project could be expanded the most. We originally intended to build a full-scale delivery drone that would be capable of carrying a pizza. We bought and built the drone, but halfway through the first semester of Senior Design, we caused an unfortunate battery incident that caught the battery on fire and triggered the first floor and basement sprinklers in the Photonics Center. This in turn destroyed our drone, closed the senior design lab for the rest of the semester, and may or may not have caused millions of dollars in water damages to expensive equipment. I suspect your future Senior Design classes will strangely over-emphasize lithiom-ion battery safety, this incident is the reason why. So our biggest piece of advice is to take their warning seriously. 

Regardless, this caused us to have to essentially restart our physical drone construction process, and so we did not have the time to build a seriously viable platform. We did do a lot of research and planning into an appropriate design. 

A couple last things to note. 

1] Flying a drone in Boston is hard because BU is quite close to the Boston-Logan airport, and there are not many free open spaces without people or cars. During the first semester we did some testing in empty South Campus parking lots when possible, and some at the Mason Square park in Brookline (about 15 minute walk from Photonics). I have also heard of research groups testing drones at Battery Park near the Microcenter in Cambridge, which is a maybe 25 minute walk from Photonics. For future groups, I would reccomend reserving or finding a real space to test, and planning days where everyone from the group can go together for a solid 8-9 hour block to test. 

2] The Mavlink/Dronekit/related drone control components are a bit of a pain to get used to. They require somewhat sensitive calibration and a lot of careful steps. Think about those ahead of time. 

3] Drone balance matters. During our in-person flight, we broke some of the legs from hard landings induced from panic because our drone was imbalanced. 

4] If you are using the NVIDIA Jetson Nano, the software installation process is a bit of a pain for three reasons: one, it is an ARM64 architcture and not an x86 architecture device which means many of your normal conveniences (Anaconda support, support for the most recent versions of libraries like PyTorch, etc.) go away; two, by default the time and date restart on startup and will not sync properly with the internet, so you need to manually set the time and date to stop web pages from refusing to connect; three, using an improperly low power source will cause the Jetson to constantly throttle itself. Stopping the last one is relatively easy, use a powerful enough barrel jack connector and make sure to set the little connector on the board to enable barrel jack power (see tutorials online). The first one can mostly be mitigated by using Archiconda, which is a conda clone for ARM64 systems (see here: https://forums.developer.nvidia.com/t/anaconda-for-jetson-nano/74286). The second one we fixed once on our first, pre-fire Nano but could never get working for the second. When you do fix it, take careful notes on how so if yours first burns down too you have the recipe to fix it.  
