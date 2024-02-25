# app.py
#Based on https://blog.miguelgrinberg.com/post/video-streaming-with-flask
#este parcha el "Expected boundary '--' not found, instead found a line of xxx bytes"

from flask import Flask, Response, request
import picamera
import io
import gevent
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)

# Flag to indicate whether the camera is in use
camera_in_use = False
camera = None  # Store the camera instance globally

@app.route('/video_feed')
def video_feed():
    global camera_in_use, camera

    if camera_in_use:
        return Response("Busy with another connection", status=503)

    camera_in_use = True

    return Response(stream_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/endconnection')
def end_connection():
    global camera_in_use, camera

    if camera_in_use:
        print("Forcing connection drop. Cleaning up resources.")
        camera.close()
        camera_in_use = False

    return "Connection dropped. Resources cleared."

def stream_frames():
    global camera

    camera = picamera.PiCamera()
    camera.resolution = (320, 240)

    try:
        while True:
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg', use_video_port=True)
            stream.seek(0)
            frame = stream.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                   b'\r\n' + frame + b'\r\n')
            gevent.sleep(0.1)  # Add a small delay to avoid high CPU usage
    except GeneratorExit:
        # Handle disconnection, clean up resources
        print("Client disconnected. Cleaning up resources.")
        camera.close()
        global camera_in_use
        camera_in_use = False

    except:
        print("Connection dropped")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

