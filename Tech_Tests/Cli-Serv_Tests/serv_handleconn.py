# app.py
from flask import Flask, Response
import picamera
import io
import gevent
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)

camera_in_use=False

@app.route('/video_feed')
def video_feed():

    global camera_in_use

    if camera_in_use:
        return Response("Busy with another connection",status=503)

    camera_in_use = True

    return Response(stream_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream_frames():
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)

    try:
        while True:
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg', use_video_port=True)
            stream.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')
            gevent.sleep(0.1)  # Add a small delay to avoid high CPU usage
    except GeneratorExit:
        # Handle disconnection, clean up resources
        print("Client disconnected. Cleaning up resources.")
        camera.close()
        global camera_in_use
        camera_in_use=False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

