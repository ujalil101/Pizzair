# Assembled System- Test Drone
<img width="567" alt="Screenshot 2024-04-27 at 1 51 59 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/8d6b44f5-1609-4a4d-bcfd-972d9d6ffacd">

# Small Drone Mechanical Hardware Schematic
Out of safety considerations, we built a small drone for algorithm testing and proof of concept and only used the large drone to show a real-life scale harness mechanism. The original basket mechanism was converted into a housing for the Jetson nano. This greatly increased in flight stability and control.

<img width="690" alt="Screenshot 2024-04-27 at 1 53 39 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/d701aa3f-73ba-432b-9529-a6af90247bd9">

# Large Drone Mechanical Hardware Schematic
A full scale drone for delivery cannot be flown without FAA approval. A concept of the large drone carrying mechanism was fabricated. Using a spring hinge and a push-to-close magnetic latch, a delivery mechanism was made. The user must set the mechanism closed first, then load the payload. Once the drone arrives at its destination. It will land, release the magnetic latch holding the spring hatch, then deposit the payload.

<img width="692" alt="Screenshot 2024-04-27 at 1 54 20 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/a531375b-c9c1-4389-8fab-89cd5f25ef24">

# Pixhawk Wiring Schematic
We connected motors, GPS module, buzzer, and safety switch with the Pixhawk, paired manual control FS-i6x transmitter and FS-iA6B receiver, and connected camera and cellular module with Jetson Nano (not shown).
<img width="355" alt="Screenshot 2024-04-27 at 1 54 55 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/32acfc82-02e5-472f-a794-b5e814397dbe">

# Connect Pixhawk to Jetson Nano Schematic
Wiring Pixhawk to Jetson required a soldered serial cable and a clear understanding of the in/out pins.

<img width="266" alt="Screenshot 2024-04-27 at 1 55 48 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/338d03df-74ca-4b5d-9993-a0617b648223">
<img width="382" alt="Screenshot 2024-04-27 at 1 55 55 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/18af519c-0052-4029-9c52-08c64e7b3868">


# Bill of Materials
The objective was to keep the cost under $3,000 per drone and we were well under control. The BOM is located in the BOM folder. 

# Drone Specifications

<img width="406" alt="Screenshot 2024-04-27 at 1 56 18 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/1b848695-5830-4739-b3db-806a46e3d782">

- Wheelbase: 450 mm
- Max take-off weight: approx. 1.8 kg
- Flight time: 10-20 minutes
- Remote distance: >= 500 meters (FS-I6X + IA6B)
- Dimensions: 14.17"L x 7.48"W x 9.84"H
- Item weight: 2.54 kg

# Power Requirements
- Battery Capacity: 4200 mAh
- Battery Cell Composition: Lithium Polymer

# Complete Drone
<img width="728" alt="Screenshot 2024-04-27 at 1 57 42 PM" src="https://github.com/ujalil101/Pizzair/assets/74789609/ccacf854-4fdc-4eaf-9135-fdc3a0e682a4">





