# This is the main file that runs the server
# It is responsible for serving the html templates and the video feed
# It also contains the list of cameras that will be served
# It serves the main page at localhost:5000

# Start the server with:
# python3 proxy_stream.py for TESTING
# gunicorn -c gunicorn_config.py app:app for PRODUCTION

from flask import Flask, render_template, Response
import cv2
import configparser

app = Flask(__name__)


# Read list of cameras from config.ini
def read_config():
    config = configparser.ConfigParser()
    config.read('cameras_config.ini')
    cameras = []
    for section in config.sections():
        camera = {
            'name': config[section]['name'],
            'address': config[section]['address'],
            
        }
        cameras.append(camera)

    return cameras


cameras = read_config()


#Generates the frames to be served
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

#entry point
@app.route('/')
def index():
    return render_template('index.html')

#Camera streaming route (processed images, needs more workers)
@app.route('/cameras_processed')
def cameras_processed():
    return render_template('cameras_processed.html', cameras=cameras)


#Camera streaming route (fast, directly from cameras)
@app.route('/cameras_fast')
def cameras_fast():
    return render_template('cameras_fast.html', cameras=cameras)


#Video feed route for camera with id=camera_id
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera = cameras[camera_id]
    camera_url = f"{camera['address']}"
    
    return Response(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    app.run(debug=True)