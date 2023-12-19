#This one implements a three-frame difference algorithm (Srivastav, 2017)to detect movement in a video stream.
#Sensitivity is improved by skipping N frames. 
# 
# Works IN THE CAMERA, not in the server.
# Needs cam config through GET request to server WIP

#USES CV2

import cv2
import numpy as np
from classes import * #helper functions
import os



def three_frame_difference():
    """This function implements a three-frame difference algorithm to detect movement.
    It uses last_frame to store the last frame so that it is accessible from /video_feed function
    It must be run on its own thread so that it does not block the main thread
    Args:
        camera_name (str): The name of the camera to be used. It must be the registered in the database.sqlite DB.
          At the same time, it must be given as an argument to the -e flag on gunicorn launch command (-e CAMERA=camera_name)

    """

    global last_frame #To store the last frame



    cam_url="http://localhost:8000/video_feed"
    
    #Open the stream
    cap = cv2.VideoCapture(cam_url) 
    recorder = VideoRecorder(cam_url) #Init recorder

    #Preload 3 consecutive frames numbered 1, 2, 3 (1st frame is discarded)
    _, frame1 = cap.read()
    _, frame2 = cap.read()
    _, frame3 = cap.read()


    #Main loop
    while True:

        #Get camera configuration AGAIN from DB so that changes are applied on each iteration LIVE
        #camera=read_config(camera_name)[0] #only the 1st result just in case

        #Apply camera configuration on each iteration
        #N= int(camera['frameskip'])
        #detectionarea = int(camera['detectionarea'])

        # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
        frame1 = frame2.copy()
        frame2 = frame3.copy()

        #Read N consecutive frames fo throw away
        #for i in range(0, N):
        #    dropFrames=cap.read() #dropFrames never used

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


        #If MASK is found, apply it to the frame. 'name' must match the camera name
        mask = cv2.imread(f"mask.jpg",cv2.COLOR_BGR2GRAY)
        if mask is None:
            print("Mask not found. Creating default mask")
            image = np.zeros((240,320),dtype=np.uint8)
            #image[:120,:]=1 #Top half of the image is '1', bottom half is '0' (image looks black)
            image[:]=1 #All image is '1' (image looks black)
            cv2.imwrite(f'mask.jpg', image)
            mask = cv2.imread(f"mask.jpg",cv2.COLOR_BGR2GRAY) #Read the mask again
        else:
            
            #We apply the m ask image to exclude image areas with "0" in the mask
            #diff = cv2.bitwise_and(diff,mask)
            threshold_diff = cv2.multiply(threshold_diff,mask) #Works with grayscale images



        # Find contours in the thresholded image
        contours, _ = cv2.findContours(threshold_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            # contourArea() method filters out any small contours
            # You can change this value
            #print(cv2.contourArea(c))
            if cv2.contourArea(c)> 10: #Sensitive to small movements
                (x, y, w, h)=cv2.boundingRect(c)
                cv2.rectangle(frame1, (x, y), (x+w, y+h), (125,225,255), 1)
                print("Movement detected")
                ###MOVEMENT DETECTION HERE###
                if not recorder.isRecording:
                    recorder.save_video_span(10)

        

        #last_frame = frame1.copy()
        #add_datetime(last_frame)
        #cv2.imshow('Frame1',last_frame)

    #cap.release()



if __name__ == "__main__" : 

    three_frame_difference()


    
