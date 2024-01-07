#This one implements a three-frame difference algorithm (Srivastav, 2017)to detect movement in a video stream.
#Sensitivity is improved by skipping N frames. 
# Database configurable.
# Accepts live DB changes
# Mask configurable. mask_{name}.jpg must exist in the same folder as this script
# Accepts live mask changes

#### This one uses the class Three_Frame_Difference from classes.py ####
# Supports stream interruption and resuming

#It streams in port 8080
# using the following routes:
# /video_feed/<int:camera_id> - returns the video stream for camera with id=camera_id



import numpy as np
from classes import * #helper functions
from flask import Flask, render_template, Response
from flask_cors import CORS
from flask import jsonify



app = Flask(__name__)
CORS(app) #To allow cross-origin requests


#--------ROUTES-------#

#entry point
@app.route('/')
def index():
    return render_template('index.html')

#Camera streaming route (processed images, needs more workers)
@app.route('/cameras_processed')
def cameras_proxied():
    return render_template('cameras_processed.html', cameras=cameras)


#Camera streaming route (fast, directly from cameras)
@app.route('/cameras_fast')
def cameras_fast():
    return render_template('cameras_fast.html', cameras=cameras)


#Video feed route for processed video using three frame difference. Uses camera id.
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(camObjs[camera_id].generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#Return a JSON array with the current cameras list
@app.route('/getcameras')
def getcameras():
    cameras = read_config_all() #read all cameras from DB
    jcameras = jsonify(cameras)
    jcameras.status_code=200
    return Response(jcameras, mimetype='application/json')



#--------MAIN-------#

cameras = read_config_all() #read all cameras from DB
camObjs = [] #list of camera objects

#Create a camera object for each camera and start loop
for cam in cameras:
    c=Three_Frame_Difference(cam['name']) #Instantiate camera object
    c.startLoop() #start the loop for each camera
    camObjs.append(c) #add to list of camera objects
    




if __name__ == "__main__" : 

    app.run(debug=False, threaded=True, port=8080) 

    
