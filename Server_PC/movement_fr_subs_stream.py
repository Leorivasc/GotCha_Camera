#This one implements a three-frame difference algorithm to detect movement in a video stream.
#Sensitivity is improved by skipping N frames.
# (Srivastav, 2017)

import cv2
import numpy as np
from classes import do_get
from classes import SQLiteDB
from classes import read_config
from flask import Flask, render_template, Response
import threading

app = Flask(__name__)
# Variable para almacenar el último frame procesado
last_frame = None
frame_lock = threading.Lock()



def three_frame_difference():
    
    global last_frame
    global name
    camera=read_config(name)[0] #only the 1st result just in case an error has two cameras with the same name
    url = f"http://{camera['ip_address']}:{camera['port']}" #url for the camera stream
    

    cap = cv2.VideoCapture(f"{url}/video_feed") #Open the stream

    #Preload 3 consecutive frames numbered 1, 2, 3 (1st frame is discarded)
    _, frame1 = cap.read()
    _, frame2 = cap.read()
    _, frame3 = cap.read()

    print("Starting 3-frame difference algorithm")

    while True:

        #Get camera configuration AGAIN from DB so that changes are applied on each iteration LIVE
        camera=read_config(name)[0] #only the 1st result just in case

        #Apply camera configuration on each iteration
        N= int(camera['frameskip'])
        detectionarea = int(camera['detectionarea'])

        # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
        frame1 = frame2.copy()
        frame2 = frame3.copy()

        #Read N consecutive frames fo throw away
        for i in range(0, N):
            dropFrames=cap.read() #dropFrames never used

        # Read new 3rd frame
        _, frame3 = cap.read()
        
        if not _:
            # No more frames to read
            break

        # Calculate difference between consecutive frames
        diffA = cv2.absdiff(frame1, frame2)
        diffB = cv2.absdiff(frame2, frame3)

        # Bitwise OR of the 2 frame differences as suggested in paper
        diff = cv2.bitwise_or(diffA, diffB)


        # Convertir la diferencia a escala de grises
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Aplicar un umbral para resaltar las diferencias
        _, threshold_diff = cv2.threshold(gray_diff, 100, 255, cv2.THRESH_BINARY)

        # Dilatar la imagen para rellenar huecos
        threshold_diff = cv2.dilate(threshold_diff, np.ones((3, 3), np.uint8), iterations=2)


        #If MASK is found, apply it to the frame
        mask = cv2.imread("mask.jpg",cv2.COLOR_BGR2GRAY)
        if mask is None:
            print("Mask failed to load")
        else:
            #We apply the mask image to exclude image areas with "0" in the mask
            #diff = cv2.bitwise_and(diff,mask)
            threshold_diff = cv2.multiply(threshold_diff,mask) #Works with grayscale images



        # Find contours in the thresholded image
        contours, _ = cv2.findContours(threshold_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            # contourArea() method filters out any small contours
            # You can change this value
            #print(cv2.contourArea(c))
            if cv2.contourArea(c)> detectionarea: #Sensitive to small movements
                (x, y, w, h)=cv2.boundingRect(c)
                cv2.rectangle(frame1, (x, y), (x+w, y+h), (125,225,255), 1)
                #print("Movement detected")
                ###MOVEMENT DETECTION HERE###


        # Mostrar el frame con las diferencias resaltadas
        #cv2.imshow(f'{name} Manual Frame Subtraction', diff)
        #cv2.imshow(f'{name} Thresholded',threshold_diff)
        #cv2.imshow(f'{name} Frame1',frame1)

        
        with frame_lock:
            last_frame = frame1.copy()

        # Salir si se presiona la tecla 'q'
        #if cv2.waitKey(30) & 0xFF == ord('q'):
        #   break

    cap.release()
    #cv2.destroyAllWindows()


def generate_frames():
    while True:
        with frame_lock:
            if last_frame is None:
                continue

            # Convertir el frame a formato JPEG para la transmisión web
            _, buffer = cv2.imencode('.jpg', last_frame)
            frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# Iniciar el hilo para procesar frames    
name = "PiZero1"
frame_thread = threading.Thread(target=three_frame_difference)
frame_thread.daemon = True
if not frame_thread.is_alive():
    frame_thread.start()


if __name__ == "__main__":
    
#inicio de la aplicación Flask solo si el hilo no está vivo
   
    app.run(debug=False, threaded=True)   

    # Ejecutar la aplicación Flask
    
