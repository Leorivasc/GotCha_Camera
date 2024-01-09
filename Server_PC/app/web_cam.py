#This one implements a three-frame difference algorithm (Srivastav, 2017)to detect movement in a video stream.
#Sensitivity is improved by skipping N frames. 
# Database configurable.
# Accepts live DB changes
# Mask configurable. mask_{name}.jpg must exist in the same folder as this script
# Accepts live mask changes

#This version works for a single camera. The name must be passed as an environment variable
#The camera name must be in the database. The script will read the rest of the configuration from the database
#The processed stream will be available at http://localhost:<mirrorport>/video_feed
#The mirrorport is also read from the database


# TO RUN:
# CAMERA=cameraname python web_cam.py
# where cameraname is the name of the camera in the database


from flask import Flask, render_template, Response
import threading
import os
from flask_cors import CORS
import classes.functions as fn
from classes.threeframedifference import Three_Frame_Difference




app = Flask(__name__)
CORS(app) #To allow cross-origin requests




@app.route('/video_feed')
def video_feed():
    return Response(cam_obj.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/snapshot')
def snapshot():
    return Response(cam_obj.snapshot(), mimetype='image/jpeg')

#### Init portion ####


#Gets the arguments from the -e flag on gunicorn ( -e camera=cameraname)
cam_env = os.getenv('CAMERA')
print(f"START Camera: {cam_env}")
cam=fn.read_config(cam_env)[0] #Read rest of the camera configuration from DB. Only the 1st result just in case.S

cam_obj = Three_Frame_Difference(cam['name']) #Create object to handle the camera

#Start thread to read frames
frame_thread = threading.Thread(target=cam_obj.three_frame_difference_loop)
frame_thread.daemon = True
if not frame_thread.is_alive():
    print("Starting thread")
    frame_thread.start()



if __name__ == "__main__" : 

    app.run(debug=False, threaded=True, port=cam['mirrorport'],host='0.0.0.0') 

    
