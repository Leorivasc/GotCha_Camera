# This is the main file that runs the main web server
# It is responsible for serving the html templates and the video feeds
# It also contains the list of cameras that will be served
# It serves the main page at http://<server_ip>:8080

# Start the server with:
# python3 web_app.py for TESTING
# gunicorn -c gunicorn_config.py app:app for PRODUCTION

#This is a standalone server that connects to ALREADY CREATED camera streams
#Those streams are local and must be created through the web_cam.py script
#This server mostly proxies the streams, so that cameras are not affected by the workers problem

from flask import Flask, render_template, Response, jsonify, send_from_directory, make_response, redirect
import cv2
from flask import request
from flask_cors import CORS
from classes.functions import * #helper functions
import socket
import os
import glob
import random
import json

app = Flask(__name__)
CORS(app) #To allow cross-origin requests



#-----------Camera streaming functions-----------------


############################################
#-----------Routes----------------#

#entry point
@app.route('/')
def index():
    #Read cookie presence
    cookiedata=read_user_cookie()

    return render_template('index.html', 
                           cookiedata=cookiedata)



#-----------Camera streaming routes-----------------

#Function to generate frames to be served locally in case of need (see /video_feed/<camera_id> route)
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


#Camera streaming route (fast, obtains directly from cameras)
@app.route('/cameras_fast')
def cameras_fast():

    #Read cookie presence
    cookiedata=read_user_cookie()

    cameras=read_config_all("isEnabled=1") #Only enabled cameras
    
    return render_template('cameras_fast.html', 
                           cameras=cameras, 
                           cookiedata=cookiedata)



#Same as above, but
#Video feed route for camera with id=camera_id (PROXY direct from cameras)
#NOT USED (only for testing, not ideal. Generates overhead and slow response only for forwarding the video feed)
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera = cameras[camera_id]
    camera_url= f"http://{camera['ip_address']}:{camera['port']}{camera['path']}"
    #camera_url = f"{camera['address']}/video_feed" #The actual feed
    
    return Response(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')



#Video feed route for processed video using three frame difference
#i.e. the video feeds are processed by the web_cam.py script for each camera. It has the mask and border drawings applied
#Those streams are served by the web_cam.py script in their mirror ports (5000+camera_id)
@app.route('/local_stream')
def local_stream():

    #Read cookie presence
    cookiedata=read_user_cookie()
    #Get a random value to avoid caching
    random_value = random.randint(1, 100) 
    cameras = read_config_all("isEnabled=1")  #Refresh enabled cameras list and config
    #Get server IP to present links properly
    host_name = socket.gethostname()+".local" #.local is needed to avoid having 127.0.0.1 as address (not used)
    #server_ip = socket.gethostbyname(host_name)
    server_ip=request.host.split(':')[0]      #Safer way to get the server IP

    #Send cameras and server data to the template for rendering
    return render_template('local_stream.html', 
                           cameras=cameras, 
                           host_name = host_name, 
                           server_ip = server_ip, 
                           random_value = random_value, 
                           cookiedata=cookiedata)
    



#-----------Recordings business routes-----------------
#Listing of camera recordings
@app.route('/list_recordings')
def file_list():

    #Read cookie presence
    cookiedata=read_user_cookie()

    # Gets the list of files in the uploads folder
    #files = os.listdir("recordings")
    os.chdir("recordings")
    files = sorted(glob.glob("*.webm"))
    thumbnails = []
    for file in files:
        thumbnails.append(file.replace(".webm",".jpg"))
    #merge in a list of lists
    filesdata = []
    for file,thumbnail in zip(files,thumbnails):
        filesdata.append([file,thumbnail])
    
    os.chdir("..")
    return render_template('list_recordings.html', 
                           filesdata=filesdata,
                           cookiedata=cookiedata)


#Downloads for recordings (allow visualizing and downloading the recordings)
@app.route('/download/<filename>')
def download_file(filename):
    # Manejar las descargas de archivos
    return send_from_directory("recordings", filename)


#Removing a recording
@app.route('/delete_recording/<filename>')
def delete_recording(filename):

    #Verify user        
    if not verify_credentials():
        return 'Unauthorized access. Please login first.'
    
    try:
        #Recordings directory
        recordings_dir = 'recordings'
        
        #Full relative path to the file
        file_path = os.path.join(recordings_dir, filename)
        thumbnail_path = os.path.join(recordings_dir, filename.replace(".webm",".jpg"))

        #Make sure the file exists
        if os.path.exists(file_path):
            #Remove the video and the thumbnail
            os.remove(file_path)
            os.remove(thumbnail_path)
            return "ok", 200
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error removing {str(e)}", 500


#-----------Mask app-----------------
#Mask app. This is a route to the mask app for a specific camera
#To be used from the local_stream.html template to open the mask app in a popup window
@app.route('/mask_app/<camera_name>')
def mask_app(camera_name):

    #Verify user        
    if not verify_credentials():
        return 'Unauthorized access. Please login first.'

    #Read cookie presence
    cookiedata=read_user_cookie()

     #Get server IP to present links properly
    host_name = socket.gethostname()
    server_ip = socket.gethostbyname(host_name)
    camera = read_config(camera_name)
    loadP5=1 #Load p5.js library

    #Notice flag to allow the loading of p5.js library
    return render_template('mask_app.html', 
                           camera=camera, 
                           host_name = host_name, 
                           server_ip = server_ip, 
                           loadP5=loadP5,
                           cookiedata=cookiedata)


# Mask upload route
@app.route('/upload_mask', methods=['POST'])
def upload_file():

    #Verify user        
    if not verify_credentials():
        return 'Unauthorized access. Please login first.'

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
#Route to ALL cameras config (table edition)
#Will respond with a simple text value

@app.route('/sys_setup')
def cameras_setup():

    #Read cookie presence
    cookiedata=read_user_cookie()

    # Check user role. Here is more sensible to check admin access
    if not verify_credentials('admin'):
        resp = make_response(redirect('/')) #Redirect to main page
        return resp
  

    #Get all cameras
    cameras = read_config_all() 
    return render_template('sys_setup.html', 
                           cameras=cameras, 
                           cookiedata=cookiedata)


#Route to return all cameras as JSON
@app.route('/getcameras_conf')
def getcameras_conf():
    cameras = read_config_all()
    jcameras = jsonify(cameras)
    jcameras.status_code=200
    return jcameras




#Template for cameras config (popups from the config button in the local_stream page)
@app.route('/camera_config/<camera_name>')
def camera_config(camera_name):

    #Read cookie presence
    cookiedata=read_user_cookie()

    try:
        camera = read_config(camera_name)[0]
    except:
        return 'Camera not found'
    
    return render_template('camera_config.html', 
                           camera=camera,
                           cookiedata=cookiedata)



# Modify cameras config route (POST ONLY)
# This route is used to modify the configuration of a camera.
# Used from the cameras_setup.html template and the camera_config.html template

@app.route('/modify_config', methods=['POST'])
def modify_config():

    # Check user role. Here is more sensible to check admin access
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    #Verify right request
    if 'name' not in request.form:
        return 'Camera name not sent'

    camera_name = request.form['name'] #Get camera name
    camera = read_config(camera_name)

    #Check if camera exists
    if not camera and request.form['name']==None:
        #Camera not found but it is a new camera or a camera renaming. We rely on id here
        return 'Camera not found'

    #Manage as dict
    data=request.form.to_dict()
   
    #Data validation before updating
    for key in data:

         ## traverse the data and change every 'on' to 1 and 'off' to 0 (checkboxes)
        if data[key] == 'on' or data[key] == 'true':
            data[key] = 1
        elif data[key] == 'off' or data[key] == 'false':
            data[key] = 0

        ##Make sure numeric values are not empty
        if data[key] == '':
            data[key] = 0


    #Perform the update
    ans = update_config(camera_name, data)

   #Return message to the client
    if ans:
        return 'Saved'
    else:
        return 'Server error'

#Route to return the email configuration as JSON
@app.route('/get_smtp_conf')
def get_smtp_conf():

    #Verify user (admin only)
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    smtp_conf = read_email_config()
    return jsonify(smtp_conf)


#Route to modify the email configuration (POST ONLY)
@app.route('/modify_smtp_conf', methods=['POST'])
def modify_smtp_conf():

    #Verify user        
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    #Manage as dict
    data=request.form.to_dict()
   
    #Data validation before updating
    for key in data:

        ##check for empty values
        print(data[key])
        if data[key] == '' or data[key] is None or data[key] == 'Null' or data[key] == 'null' or data[key] == 'undefined':
            return "Some empty values"

         ## traverse the data and change every 'on' to 1 and 'off' to 0 (checkboxes)
        if data[key] == 'on' or data[key] == 'true':
            data[key] = 1
        elif data[key] == 'off' or data[key] == 'false':
            data[key] = 0

        ##Make sure numeric values are not empty
        if data[key] == '':
            data[key] = 0

    #Perform the update
    ans = update_email_config(data)

    if ans:
        return 'Modified'
    else:
        return 'Server error'

# Route to handle configuration modification requests from W2UI table
# This route handles both GET and POST requests,since W2UI sends requests using both methods
# The request is sent as a JSON string in the 'request' key of the request.args data
# The request is parsed and the appropriate action is taken
    
@app.route('/w2ui_db', methods=['GET','POST'])
def w2ui_db():
    
    #Verify user        
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'
    
    #Get the request method and values
    method = request.method
    records = read_config_all()
    requested = json.loads(request.args.get('request'))
    
    #If method was GET, i.e. the request was sent as a query string
    #which is the case when W2UI sends every request
    if method == 'GET':
        #Just return the full list of records (default limits to 100)
        if requested['limit']:
            limit = int(requested['limit'])
            records = records[:limit]

            #Return the full list of records in W2UI format
            response = {'status': 'success', 'total': len(records), 'records': records}
            return response, 200

    #If method was POST, handle the request
    #notice this request also has a 'request' key in request.args data
    elif method == 'POST':
        data = request.form.to_dict()
        action=requested['action']

        #Handle the delete request
        if action=='delete':
             #Assuming recid is in the form "recid-<id>" (from the table), +1 because it is 0-indexed
            recid = int(requested['recid'][0].split('-')[1])  
            cam_name = records[recid]['name']
            delted = remove_camera(records[recid]['name'])
            response = {'status': 'success'}
            return jsonify(response), 200

        elif requested == 'get-records':
            # Get the records from the database and send them back to the client
            records = read_config_all()
            response = {'status': 'success', 'total': len(records), 'records': records}
            return jsonify(response), 200
        
        



#-----------Camera management routes-----------------
#Route to add new cameras (POST ONLY). 
#To be used from the W2UI table in the cameras_setup.html template.
#These handle the custom JS event handlers to add and delete cameras
        
@app.route('/add_camera', methods=['POST'])
def add_camera():

    #Verify user
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    #Verify right request
    if 'name' not in request.form:
        return 'Camera name not sent'

    camera_name = request.form['name']
    camera = read_config(camera_name)

    #Check if camera exists
    if camera:
        return 'Camera already exists'

    #Manage as dict
    data=request.form.to_dict()
   
    #Data validation before updating
    for key in data:
    
        #Make sure numeric values are not empty
        if data[key] == '':
            return "Some empty values"

    #Perform the insertion
    ans = new_camera(data)

    if ans:
        return 'Added'
    else:
        return 'Error'

#Remove camera (POST ONLY)
@app.route('/delete_camera', methods=['POST'])
def delete_camera():

    #Verify user
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    #Verify right request
    if 'name' not in request.form:
        return 'Camera name not sent'

    camera_name = request.form['name']
    camera = read_config(camera_name)

    #Check if camera exists
    if not camera:
        return 'Camera not found'

    #Perform the update
    ans = delete_camera(camera_name)

    if ans:
        return 'Deleted'
    else:
        return 'Error'


#-------User login/logout routes, functions-----------------
#Admin login route
@app.route('/login', methods=['POST'])
def login():

    #Verify right request
    if 'password' not in request.form:
        return 'Password not sent'

    user = request.form['user']
    password = request.form['password']

    #Check user
    if not is_user(user):
        return "User/password incorrect"

    #Check password (password is stored in hashed form in the database)
    storedpass= get_user(user)[0]['password']
    password = md5hash(password) #Hash the password
    if password==storedpass:
        resp = make_response("Ok")
        resp.set_cookie('data', password,max_age=86400) #Set cookie with the hashed password
        resp.set_cookie('user', user,max_age=86400)     #Same for username
        return resp
    else:
        return "User/password incorrect"
        

#Logout route
#This route deletes the user and data cookies
@app.route('/logout')
def logout():
    resp = make_response(redirect(request.referrer) )
    resp.delete_cookie('user')
    resp.delete_cookie('data')
    resp.headers['Location'] = request.referrer
    resp.status_code = 302
    return resp


#Read cookie and return a given 'else' value if not found
def read_user_cookie():
    #Read cookies
    data = request.cookies.get('data')
    user = request.cookies.get('user')
        
    #If any not found, return a default value
    if data is None or user is None:
        data='0'
        user='Guest'

    return (user, data)

#Compare cookie data against stored user/passeword to verify valid credentials
def verify_credentials(testuser='admin'):
    #Read cookies
    data = request.cookies.get('data')
    user = request.cookies.get('user')

    #If any not found, return a default value
    if data is None or user is None:
        return False
    
    #if the user is not the testuser, return False
    if user != testuser:
        return False

    dbpass=get_user(user)[0]['password']
    if data == dbpass:
        return True  #User is logged in and verified
    else:
        return False #Stored password does not match the one in the database

#Route to change Admin password
@app.route('/change_admin_password', methods=['POST'])
def change_password():
    
    #Verify user
    if not verify_credentials('admin'):
        return 'Unauthorized access. Please login first.'

    #Verify right requests
    if 'currentPassword' not in request.form:
        return 'Current password not sent'

    if 'newPassword' not in request.form:
        return 'New password not sent'

    #Check that old password matches with the stored one
    oldpassword = request.form['currentPassword']
    oldpassword = md5hash(oldpassword)
    storedpass= get_user('admin')[0]['password']
    if oldpassword != storedpass:
        return "Old password incorrect"
    
    #Get new password    
    newpassword = request.form['newPassword']
    
    #Hash the new password for storing
    password = md5hash(newpassword)

    #Perform the update
    ans = update_password('admin', password)

    if ans:
        return 'Password updated'
    else:
        return 'Error storing new password'


#-----------Error handling-----------------
#Error handling
@app.errorhandler(404)
def page_not_found(e):
    return 'Not found', 404


#-----------Main-----------------
cameras = read_config_all("isEnabled=1") #Only enabled cameras

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8080, host='0.0.0.0')