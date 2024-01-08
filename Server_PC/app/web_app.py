# This is the main file that runs the server
# It is responsible for serving the html templates and the video feed
# It also contains the list of cameras that will be served
# It serves the main page at localhost:5000

# Start the server with:
# python3 proxy_stream.py for TESTING
# gunicorn -c gunicorn_config.py app:app for PRODUCTION

#This is a standalone server that connects to ALREADY CREATED camera streams
#Those streams are local and must be created through the web_cam.py script
#This server mostly proxies the streams, so that cameras are not affected by the workers problem

from flask import Flask, render_template, Response, jsonify
import cv2

from classes.functions import * #helper functions
import socket

app = Flask(__name__)

#-----------Functions-----------------




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


#-----------Routes-----------------

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


#Video feed route for camera with id=camera_id (PROXY)
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera = cameras[camera_id]
    camera_url= f"http://{camera['ip_address']}:{camera['port']}{camera['path']}"
    #camera_url = f"{camera['address']}/video_feed" #The actual feed
    
    return Response(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')

#Video feed route for processed video using three frame difference
@app.route('/video_local_stream')
def video_local_stream():

    #Get server IP to present links properly
    host_name = socket.gethostname()
    server_ip = socket.gethostbyname(host_name)

    #Send cameras and server data to the template
    return render_template('cameras_local_stream.html', cameras=cameras, host_name = host_name, server_ip = server_ip)
    


#Return a JSON array with the current cameras list
@app.route('/getcameras')
def getcameras():
    jcameras = jsonify(cameras)
    jcameras.status_code=200
    return jcameras


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8080, host='0.0.0.0')