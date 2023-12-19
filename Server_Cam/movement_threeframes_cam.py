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

    #Recording to video file
    doRecord=False
    dateBuffer= ThingBuffer() #Buffer to store the date to be used in the video filename
    iniTimeBuffer=ThingBuffer() #Buffer to store the initial time of the recording
    duration=10 #Duration of the recording in seconds
    
    # Configure video recording
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 25.0
    video_out = cv2.VideoWriter("alarm.avi", fourcc, fps, (320,240))  # Resolution


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

        framex=frame1.copy()
        #framey=frame2.copy()
        #framez=frame3.copy()
        #Traverse all contours finding areas greater than a threshold
        #If an area is found, draw a rectangle around it
        #set doRecord to True to start recording
        for c in contours:
            # contourArea() method filters out any small contours
            # You can change this value
            #print(cv2.contourArea(c))

            if cv2.contourArea(c)> 64:      #Sensitivity in square pixels
                (x, y, w, h)=cv2.boundingRect(c)
                

                framex=cv2.rectangle(framex, (x, y), (x+w, y+h), (125,225,255), 1)
                #framey=cv2.rectangle(framey, (x, y), (x+w, y+h), (125,225,255), 1)
                #framez=cv2.rectangle(framez, (x, y), (x+w, y+h), (125,225,255), 1)


                if not doRecord:
                    print("Recording started")
                    doRecord=True #Start recording flag
                    #store date as a string in the buffer
                    dateBuffer.store(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")) #Store the date to be used in the video filename
                    iniTimeBuffer.store(cv2.getTickCount()) #Store the initial time of the recording
                

        if doRecord:


            new_filename=f'alarm_{dateBuffer.get()}.avi' #Get the date from the buffer, keeped until unlocked
            

            #Record
            framex = add_datetime(framex) #Add datetime to the frame
            #framey = add_datetime(framey) #Add datetime to the frame
            #framez = add_datetime(framex) #Add datetime to the frame
            video_out.write(framex) #Write frame to video
            #video_out.write(framey) #Write frame to video
            #video_out.write(framez) #Write frame to video
            
            #Breaks after 'duration' seconds
            current_time = cv2.getTickCount()
            time_passed = (current_time - iniTimeBuffer.get()) / cv2.getTickFrequency()
            
            #print(time_passed) #DEBUG
            if time_passed > duration:
                video_out.release()
                doRecord=False
                print("Recording finished")
                dateBuffer.unlock() #Unlock the buffer
                iniTimeBuffer.unlock() #Unlock the buffer
                os.rename("alarm.avi",new_filename)


        #Opens in window
        #cv2.imshow('Video', frame1)


if __name__ == "__main__" : 

    three_frame_difference()

#Probar con thread. aparentemente e loop pierde tiempo en el chequeo de contornos.
#Lo malo es que se pierde la capacidad de guardar el frame con los contnrnos dibujados
#thread1 = threading.Thread(target=record_whatever, args=(1,))
#thread1.start()
#Se puede copiar la tecnica del frame_lock de server_pc