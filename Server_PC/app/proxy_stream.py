#

from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# Lista de cámaras con sus direcciones IP y puertos
cameras = [
    {"nombre": "PiZero1", "direccion_ip": "http://pizero1.local", "puerto": "8000"},
    {"nombre": "Pi2", "direccion_ip": "http://pi2.local", "puerto": "8000"},
    #{"nombre": "Laptop", "direccion_ip": "http://leo.local", "puerto": "5000"},
    # Agrega más cámaras según sea necesario
]

#entry point
@app.route('/')
def index():
    return render_template('index.html')

#Camera streaming route
@app.route('/cameras')
def cameras_url():
    return render_template('cameras.html', cameras=cameras)


@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera = cameras[camera_id]
    camera_url = f"{camera['direccion_ip']}:{camera['puerto']}/video_feed"
    
    
    return Response(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')



#These are the frames that we will be serving.
#The convenient format is bytes, so that they are rendered in the html template
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


if __name__ == '__main__':
    app.run(debug=True)