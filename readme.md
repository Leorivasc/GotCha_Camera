# GotCha!

## Surveillance Camera

This repository contains the GotCha! project files for the Final Project module on the BSc Computer Science at University of London, 2024.

The software is basically divided into two main folders:

1. **Server_PC**: Holds the files and folders to run on the PC side, providing the following functions:
   1. The web server with all their required files
   2. The image processing (the movement detection routines)
   3. The alerting (turning lights on, sounding an alarm in the cameras) by sending them the alert signals; the email notification sending
   4. The video recording and storing
   5. The main configuration database
2. **Server_Cam**: Holds the files and folders to run on the CAMERA side (Raspberry Pi) to provide the following functions:
   1. Generating a web streaming on port 8000
   2. Web serving a small page to present the stream
   3. Provide http entries as an API to send orders and get statuses
   4. Provide the GPIO outputs to generate actions on the real world (controlling an LED, turning a light or sound alarm on/off)
   5. Provide a simple equivalent script to run on PC or any other Python3 and camera-enabled device (laptop, PC with USB camera) 
3. **Tech_Tests**: Much of the research and testing produced a bunch of files with useful routines, techniques and other interesting scripts that didn't make it to the final release. All of them are kept here for reference.

------

**To setup Server**

Download the repository. In this case, only the **Server_PC** folder is needed.

1. Create a Python virtual environment and activate it

   `python -m venv VENV`
   `cd VENV`
   `source bin/activate`

2. Go to Server_PC folder and install dependencies

   `cd Server_PC`

   `pip install -r app/requirements.txt`

3. Run the server

   `python launch.py`


