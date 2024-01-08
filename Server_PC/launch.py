#This launcher is used to run the app in a production environment
#It will launch a gunicorn process for each camera in the database

#Use: python launch.py

#Will open a flask webserver for each camera and a gunicor server for the website

import subprocess
import os
from app.classes import *
from app.classes.functions import *
from app import *

#Change current dir to app. It all happens in the app folder
os.chdir("app")
#Prepare and read cameras config database
cameras = read_config_all() #Read all enabled cameras


#Prepare gunicorn command
#camera_app command will be executed for each camera in the database
camera_app="python web_cam.py"
#website_app command will be executed for the website
website_app = "gunicorn -c web_gunicorn_config.py web_app:app"


# Starts each camera and website
def run_scripts():
    processes = []

    #Run cameras
    #TODO: Add a check to see if the camera is already running
    #Will traverse the cameras list and start a process for each camera
    for camera in cameras:
        camera_id = camera['id']
        camera_name = camera['name']
        camera_ip = camera['ip_address']
        mirror_port = camera['mirrorport']


        try:
            #command = f"{camera_app} --bind 0.0.0.0:{mirror_port} --env CAMERA={camera_name}"
            command = f"CAMERA={camera_name} {camera_app}"
            proc = subprocess.Popen(command, shell=True)
            processes.append(proc)
            print(f"Process {camera_name} started")
        except Exception as e:
            print(f"Camera {camera_name} failed to start: {e}")

    # Run the website
    #TODO: Add a check to see if the website is already running
    #Will start a process for the website
    try:
        proc = subprocess.Popen(website_app, shell=True)
        processes.append(proc)
        print(f"Process website started")
    except Exception as e:
        print(f"Process webserver failed to start: {e}")

    # Wait for all processes to finish
    for proc in processes:
        proc.wait()
        pass

if __name__ == "__main__":
    run_scripts()
