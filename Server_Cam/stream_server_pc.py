#FLASK APP. Standalone.Serves video streaming. Useful for PC camera. Lightweight.
#Uses Flask, OpenCV
#To run: python3 stream_server_pc.py
#To access: http://localhost:8000/video_feed
#NO templates provided. Just the video feed. Status/Alarm/Clear endpoints provided.
#No actual actions implemented

from flask import Flask, render_template, Response, send_from_directory
import cv2
import time

PAGE="""\
<html>
<head>
<title>GotCha PI Streaming</title>
</head>
<body>
<h1>GotCha! PC Streaming</h1>
<img src="/video_feed" width="320" height="240" />
</body>
</html>
"""

app = Flask(__name__)
cap = cv2.VideoCapture(0)
####PC CAMERA MAY REFUSE TO CHANGE RESOLUTION USING cap.set()####
cap.set(3, 320)  # Width
cap.set(4, 240)  # Height


#Get hostname
import socket
hostname = socket.gethostname().split('.')[0] #Just the name

#Alert flag
isAlert = False #Mostly to comply with the API


#Frames for video feed
def generate_frames():
    while True:
        try:
            time.sleep(0.083) #12fps
            # Lee un cuadro de la cámara
            success, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) ## Color correct for cv2, or else it looks blue in some cameras (?)
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




#Returns the main page with the video feed
@app.route('/')
def index():
    return PAGE



@app.route('/status')
def status():
    content = '{'+\
        '"hostname":'+'"'+hostname\
        +'"'+',"connections":'+'"'+"0"\
        +'"'+',"led":'+'"'+"No Led"\
        +'"'+',"relay":'+'"'+"No relay"\
        +'"'+',"alert":'+'"'+str(isAlert)\
        +'"'+'}'
    return Response(content, mimetype='application/json')


#Simulate an alarm
@app.route('/alarm')
def alarm():
    global isAlert
    isAlert = True
    return "ALARM!"

#Clear the simulated alarm
@app.route('/clear')
def clear():
    global isAlert
    isAlert = False
    return "ALL CLEAR!"




if __name__ == '__main__':
    app.run(debug=False, port=8000, bind='0.0.0.0')

