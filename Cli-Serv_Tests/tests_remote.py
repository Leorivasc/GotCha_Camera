import cv2
import tkinter as tk
import time
import threading
import pygame.mixer as mixer

def play_mp3(nombre_archivo):
    # Inicializa el mezclador de audio de pygame
    mixer.init()

    # Crea un objeto de sonido
    sonido = mixer.Sound(nombre_archivo)

    # Reproduce el sonido en una hebra separada
    def reproducir():
        sonido.play()

    # Crea una hebra para reproducir el sonido
    hilo_reproduccion = threading.Thread(target=reproducir)

    # Inicia la hebra
    hilo_reproduccion.start()
    
#Draws a yellow square around the given pixel
def drawYellowSquare(frame,pixel):
    cv2.rectangle(frame, (pixel[0]-2, pixel[1]-2), (pixel[0]+2,pixel[1]+2), (0,255,255), 2)
    #return frame

def drawRedSquare(frame,pixel):
    cv2.rectangle(frame, (pixel[0]-2, pixel[1]-2), (pixel[0]+2,pixel[1]+2), (0,0,255), 2)
    #return frame



video=cv2.VideoCapture("http://127.0.0.1:5000/video_feed")


# Configura el tamaño del frame (Pi zero)
video.set(3, 320)  # Ancho
video.set(4, 240)  # Alto

# Check if the video opened successfully
if (video.isOpened()== False): 
    print("Error opening video file")
    

initial_frame = None
hits=0
detected=False
fresh_frame=False

zero_counter = 0
frame_count = 0



#popup=tk.Tk()
#popupLabel=tk.Label(popup,text="LaVentana")
#popupLabel.pack()
#popup.mainloop()


#init loop (macOS)
_,dummy=video.read()
while dummy.shape[0]==180:
    _,dummy = video.read()


# We start an infinite loop and keep reading frames from the webcam until we press 'q'
while True:
    check, frame = video.read()
    
    #frame = cv2.resize(frame, (int(frame.shape[0]*0.5), int(frame.shape[1]*0.5)), interpolation=cv2.INTER_AREA)
    
    if check==False:
        print("Video ended")
        break
    
    cv2.imshow("JUST READ",frame)

    # Gray conversion and noise reduction (smoothening)
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur_frame=cv2.GaussianBlur(gray_frame,(13,13),0)

    
    # The first captured frame is the baseline image
    if initial_frame is None:
        initial_frame = blur_frame
        

    #Lets refresh reference frames every 5seg
    if int(time.time())%2==0 and fresh_frame==False:
        initial_frame = blur_frame
        #print("Forced refresh")
        fresh_frame=True
        



    # The difference between the baseline and the new frame
    delta_frame=cv2.absdiff(initial_frame,blur_frame)
    
    #Let's blur the difference image a bit more to make some car features dissapear
    delta_frame = cv2.GaussianBlur(delta_frame, (3,3), 0)
    
    #Thresholding THRESH_BINARY, THRESH_TOZERO
    threshold_frame=cv2.threshold(delta_frame,10,255, cv2.THRESH_BINARY)[1]
    
   
    # The cv2.findContours() method we will identify all the contours in our image.
    # This method expects 3 parameters, (a) image, (b) contour retrieval mode and
    # (c) contour approximation method
    (contours,_)=cv2.findContours(threshold_frame,cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_NONE)
    
    #Draw all contours
    #cv2.drawContours(frame,contours,-1,(255,0,0),3)
    

    for c in contours:
        # contourArea() method filters out any small contours
        # You can change this value
        if cv2.contourArea(c) > 10000:
            
            #(x, y, w, h)=cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
            #cv2.drawContours(frame,[c],-1,(0,255,0),1)
            pass
        
    
    
    #Multiplica para evitar una parte de la imagen
    mask = cv2.imread("mask.jpg",cv2.COLOR_BGR2GRAY)
    if mask is None:
        print("Mask failed to load")
    #mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    #print("mask "+str(mask.shape))
    result_masked = cv2.multiply(threshold_frame,mask)
    #print("result mult "+str(result_mult.shape))
        
        
        
        
        
    #Define pixels to check
    #pixels = [[100,100],[150,100],[200,100],[200,200],[150,150],[100,150],[100,200],[200,150],[150,200]]
    #coordinates every 10 pixels
    pixels = [[10,20],[20,20],[30,20],[40,20],[50,20],[60,20],[70,20],[80,20],[90,20],[100,20],[110,20],[120,20],[130,20],[140,20]]
    
    #draw red boxes around pixels
    for p in pixels:
        drawRedSquare(frame,p)


    #loop through pixels and check if they are white. Sound alert if so
    for p in pixels:
        pix = result_masked[p[1],p[0]] #For some reason, x and y are inverted
        if pix>50: # and detected==False:
            hits=hits+1
            #print("HIT "+str(p))
            play_mp3("ping.mp3")
            detected=True
            fresh_frame=False
            drawYellowSquare(frame,p) #draw yellow square around touched pixel
        else:
            detected=False
            #initial_frame = blur_frame #fail to detect slow moving elements
            






    
    # To better understand the application, we can visualise the different frames generated
    cv2.imshow('Main view', frame)
    #cv2.imshow('Baseline image', initial_frame)
    #cv2.imshow("Gray Frame",gray_frame)
    #cv2.imshow('Delta frame', delta_frame)   
    cv2.imshow('Threshold frame', threshold_frame)
    cv2.imshow('Masked frame', result_masked)    

    #print("threshold frame "+str(threshold_frame.shape))
    #print("frame "+str(frame.shape))
    

    # Stop the program by pressing 'q'    
    if cv2.waitKey(1) &0xFF == ord('q'):
        break
    
    
    
    
    

# After the loop release the video object
video.release()

# Destroy all the windowsq
cv2.destroyAllWindows()
