#This one implements a three-frame difference algorithm to detect movement in a video stream.
#Sensitivity is improved by skipping N frames.
# (Srivastav, 2017)

import cv2
import numpy as np

cap = cv2.VideoCapture("http://192.168.1.13:8000/video_feed")

#Preload 3 consecutive frames numbered 1, 2, 3
_, frame1 = cap.read()
_, frame2 = cap.read()
_, frame3 = cap.read()

N=0 #Number of frames to skip

while True:

    # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
    frame1 = frame2.copy()
    frame2 = frame3.copy()

    #Read N consecutive frames fo throw away
    for i in range(0, N):
        dropFrames=cap.read()

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
        print(cv2.contourArea(c))
        if cv2.contourArea(c)> 20: #Sensitive to small movements
            (x, y, w, h)=cv2.boundingRect(c)
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (125,225,255), 1)


    # Mostrar el frame con las diferencias resaltadas
    cv2.imshow('Manual Frame Subtraction', diff)
    cv2.imshow('Thresholded',threshold_diff)
    cv2.imshow('Frame1',frame1)



    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
