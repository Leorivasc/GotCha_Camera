# This is the main file that runs the server
# It is responsible for serving the html templates and the video feed
# It also contains the list of cameras that will be served
# It serves the main page at localhost:8080

# Start the server with:
# python3 web_app.py for TESTING
# gunicorn -c gunicorn_config.py app:app for PRODUCTION

#This is a standalone server that connects to ALREADY CREATED camera streams
#Those streams are local and must be created through the web_cam.py script
#This server mostly proxies the streams, so that cameras are not affected by the workers problem

from flask import Flask, render_template, Response, jsonify, send_from_directory
import cv2
from flask import request
from flask_cors import CORS
from classes.functions import * #helper functions
import socket
import os
import glob
import random

app = Flask(__name__)
CORS(app) #To allow cross-origin requests


#Generates the frames to be served locally
def generate_frames(camera_url):
    cap = cv2.VideoCapture(camera_url)
    
    while True:
        success, frame = cap.read()
        
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + f"{len(frame_bytes)}".encode() + b'\r\n'
                   b'\r\n' + frame_bytes + b'\r\n')
    cap.release()

###################################
#-----------Routes----------------#

cameras = read_config_all()

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



#Video feed route for camera with id=camera_id (PROXY direct from cameras)
#NOT USED (only for testing)
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera = cameras[camera_id]
    camera_url= f"http://{camera['ip_address']}:{camera['port']}{camera['path']}"
    #camera_url = f"{camera['address']}/video_feed" #The actual feed
    
    return Response(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')



#Video feed route for processed video using three frame difference
#i.e. the video feed is processed by the web_cam.py script, so it has the mask and border drawings
#it redirects to 'mirror' ports.
@app.route('/local_stream')
def video_local_stream():
    random_value = random.randint(1, 100) #To avoid caching
    cameras = read_config_all() #Refresh cameras list and config
    #Get server IP to present links properly
    host_name = socket.gethostname()+".local" #.local is needed to avoid having 127.0.0.1 as address (not used)
    server_ip = socket.gethostbyname(host_name)

    #Send cameras and server data to the template
    return render_template('local_stream.html', cameras=cameras, host_name = host_name, server_ip = server_ip, random_value = random_value)
    


#Return a JSON array with the current cameras list
@app.route('/getcameras')
def getcameras():
    jcameras = jsonify(cameras)
    jcameras.status_code=200
    return jcameras


#-----------Recordings routes-----------------
#Listing of camera recordings
@app.route('/list_recordings')
def file_list():
    # Gets the list of files in the uploads folder
    #files = os.listdir("recordings")
    os.chdir("recordings")
    files = sorted(glob.glob("*.webm"))
    thumbnails=sorted(glob.glob("*.jpg"))
    #merge in a list of lists
    filesdata = []
    for file,thumbnail in zip(files,thumbnails):
        filesdata.append([file,thumbnail])
    
    os.chdir("..")
    return render_template('list_recordings.html', filesdata=filesdata)

#Downloads for recordings
@app.route('/download/<filename>')
def download_file(filename):
    # Manejar las descargas de archivos
    return send_from_directory("recordings", filename)


#-----------Mask app-----------------
#Mask app
@app.route('/mask_app/<camera_name>')
def mask_app(camera_name):
     #Get server IP to present links properly
    host_name = socket.gethostname()
    server_ip = socket.gethostbyname(host_name)
    camera = read_config(camera_name)

    return render_template('mask_app.html', camera=camera, host_name = host_name, server_ip = server_ip)

# Mask upload route
@app.route('/upload_mask', methods=['POST'])
def upload_file():
    #Verify right request
    if 'mask' not in request.files:
        return 'File not sent'

    file = request.files['mask']

    # Check empty filename
    if file.filename == '':
        return 'No filename'

    #Check permitted file type
    if file and file.filename.endswith(".jpg"):
        #Proceed to save file
        filename = file.filename
        file.save(os.path.join("masks", filename))
        return 'File uploaded successfully'

    return 'File not allowed'


#-----------Config routes-----------------
#Template for cameras config
@app.route('/camera_config/<camera_name>')
def cameras_config(camera_name):
    try:
        camera = read_config(camera_name)[0]
    except:
        return 'Camera not found'
    
    return render_template('camera_config.html', camera=camera)


###TEST###
@app.route('/camera_config_inc/<camera_name>')
def cameras_config_inc(camera_name):
    try:
        camera = read_config(camera_name)[0]
    except:
        return 'Camera not found'
    
    return render_template('camera_config_inc.html', camera=camera)



# Modify cameras config route (POST ONLY)
@app.route('/modify_config', methods=['POST'])
def modify_config():
    #Verify right request
    if 'name' not in request.form:
        return 'Camera name not sent'

    camera_name = request.form['name']
    camera = read_config(camera_name)

    #Check if camera exists
    if not camera:
        return 'Camera not found'



    #Update config
    data=request.form.to_dict()
    ## traverse the data and change every 'on' to 1 and 'off' to 0 (checkboxes)
    for key in data:
        if data[key] == 'on':
            data[key] = 1
        elif data[key] == 'off':
            data[key] = 0

    ans = update_config(camera_name, data)

    if ans:
        return 'Updated'
    else:
        return 'Error'



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8080, host='0.0.0.0')