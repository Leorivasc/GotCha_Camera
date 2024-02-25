#This server implements a three-frame difference algorithm (Srivastav, 2017)to detect movement in a video stream.
#Sensitivity is improved by skipping N frames. 
# Database configurable.
# Accepts live DB changes
# Mask configurable. mask_{name}.jpg must exist in the same folder as this script
# Accepts live mask changes

#This version works for A SINGLE camera. The name must be passed as an environment variable
#The camera name must be in the database. The script will read the rest of the configuration from the database
#The processed stream will be available at http://<server_host>:<mirrorport>/video_feed
#The mirrorport is also read from the database and it should be unique for each camera, in the range 5000...5000+<id of the last camera>


# TO RUN:
# CAMERA=cameraname python web_cam.py
# where cameraname is the name of the camera in the database


from flask import Flask, Response
import threading
import os
from flask_cors import CORS
import classes.functions as fn
from classes.videorecorder import VideoRecorder
from classes.alerting import Alerting
from classes.processmovement import ProcessMovement
import json
import socket

app = Flask(__name__)
CORS(app) #To allow cross-origin requests



#----- Camera image and recording routes--------------------

#Main streaming route
@app.route('/video_feed')
def video_feed():
    return Response(processor_cam_obj.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




#Snapshot route. Returns a single frame from the processed stream(used in the mask app)
#It will include the movement detection markers (rectangles)
@app.route('/snapshot')
def snapshot():
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #return Response(processor_cam_obj.snapshot(), mimetype='image/jpeg')

    response = Response(processor_cam_obj.getSnapshot(), mimetype='image/jpeg')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response



#----- Video recording routes--------------------

#Sends the start recording command to the recorder object
@app.route('/startrecording')
def startrecording():

    recorder_obj.startRecording()
    response = Response("Recording started")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


#Sends the stop recording command to the recorder object
@app.route('/stoprecording')
def stoprecording():

    recorder_obj.stopRecording()
    response = Response("Recording stopped")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




#-----Trigger actions routes--------------------

@app.route('/alarm/<int:seconds>')
def alarm(seconds):
    alert_obj.startAlert(seconds)
    response = Response("Manual alert triggered")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/clear')
def clear():
    alert_obj.stopAlert()
    response = Response("Manual alert cleared")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

## -------Test routes ------------
@app.route('/restart')
def restart():
    processor_cam_obj.restartLoop()
    response = Response("Loop restarted")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/stop')
def stop():
    processor_cam_obj.stopLoop()
    response = Response("Loop stopped")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


##--- Object state routes ------
def getstateJSON():
    
        states = {
            "loopOK": processor_cam_obj.getState(), 
            "videoIsRecording": recorder_obj.isRecording(),
            "processedVideoIsRecording": processedRecorder_obj.isRecording() ,
            "isAlerting": alert_obj.isAlerting()
            }
        
        statesJSON = json.dumps(states)   
        return statesJSON

def getStateHTML():
    # Parse the JSON data
    states = json.loads(getstateJSON())

    # Create the HTML table
    table_html = "<table>"
    table_html += "<tr><th>Loop OK</th><th>Video Is Recording</th><th>Processed Video Is Recording</th><th>Is Alerting</th></tr>"
    table_html += f"<tr><td>{states['loopOK']}</td><td>{states['videoIsRecording']}</td><td>{states['processedVideoIsRecording']}</td><td>{states['isAlerting']}</td></tr>"
    table_html += "</table>"

    return table_html


@app.route('/getstate')
#gets state in json format
def getstate():

    statesJSON=getstateJSON()
    response = Response(statesJSON)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Content-Type', 'application/json')
    return response



@app.route('/getstatehtml')
#gets state in html format
def getstatehtml():
    response = Response(getStateHTML())
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Content-Type', 'text/html')
    return response






#### Init portion ####
#Gets the arguments from the -e flag on gunicorn ( -e camera=cameraname)

cam_env = os.getenv('CAMERA')
print(f"START Camera: {cam_env}")
cam=fn.read_config(cam_env)[0] #Read rest of the camera configuration from DB. Only the 1st result just in case.S


#Get server IP to present links properly (gallery and email links)
host_name = socket.gethostname()+".local"
server_ip = socket.gethostbyname(host_name)
web_app_port = 8080 #Default port for the web app (hardcoded)
web_app_url = f"http://{server_ip}:{web_app_port}" #URL for the web app


#Instantiate objects for 'this' camera. Videorecorder and alerting. 
recorder_obj = VideoRecorder(cam['name']) #Create object to handle the video recorder
processedRecorder_obj = VideoRecorder(cam['name'],"Processed_") #Create object to handle the video recorder for processed video


#Create object to handle the alerting. Notice app context is passed to the email sender
#It will also use the recorder object to gain access to last thumbnails and video files if needed
#It will also use the web_app_url to create links in the email
alert_obj = Alerting(cam['name'],app,recorder_obj, web_app_url) 

#Instantiate processor object for 'this' camera. ProcessMovement. Uses the recorder and alerting objects
processor_cam_obj = ProcessMovement(cam['name'], recorder_obj,processedRecorder_obj ,alert_obj) #Create object to handle the camera
processor_cam_obj.startLoop() #Start the loop to process frames


""" #Start thread to read frames
frame_thread = threading.Thread(target=processor_cam_obj._main_loop)
frame_thread.daemon = True
if not frame_thread.is_alive():
    print("Starting thread")
    frame_thread.start() """



if __name__ == "__main__" : 

    app.run(debug=False, threaded=True, port=cam['mirrorport'],host='0.0.0.0') 

    
