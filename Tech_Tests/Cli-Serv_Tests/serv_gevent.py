#This one uses gevent worker to allow keepalive connection

from flask import Flask, Response
import picamera
import io

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)

    while True:
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

