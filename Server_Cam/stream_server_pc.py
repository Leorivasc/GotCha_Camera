#FLASK APP. Standalone.Serves video streaming. Useful for PC camera.
#Uses Flask, OpenCV
#To run: python3 stream_server_pc.py
#To access: http://localhost:8000/video_feed
#NO templates provided. Just the video feed.

from flask import Flask, render_template, Response, send_from_directory
import os

import cv2

app = Flask(__name__)
cap = cv2.VideoCapture(0)
####PC CAMERA REFUSES TO CHANGE RESOLUTION USING cap.set()####
cap.set(3, 320)  # Ancho
cap.set(4, 240)  # Altura


#Frames for video feed
def generate_frames():
    while True:
        try:
            # Lee un cuadro de la cámara
            success, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) ## Correct color for cv2, or else it looks blue in some cameras
            ##16:9=640,360
            frame = cv2.resize(frame, (320, 240)) ####FORCE RESIZE (pc camera refuses to change resolution using cap.set())
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error reading from camera or color correcting, will pass... {e}")
            pass

#Route for video
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




# Ruta para cargar la página inicial
@app.route('/')
def index():
    return render_template('index.html')

   

# Ruta para servir archivos estáticos (HTML, JS, CSS, imágenes, etc.)
@app.route('/mask_app/<path:filename>')
def serve_static(filename):
    return send_from_directory('mask_app', filename)




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

