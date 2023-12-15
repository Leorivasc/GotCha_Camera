#Based on Intelligent Signal Processing module course material
#This one selects several triggering pixels and sends a GET request to the server when they are touched
#It also sends a GET request to clear the alarm when a reset pixel is touched
#It also draws a yellow square around the touched pixel


import cv2
import time
import requests
import threading

#Performs quick and dirty GET requests
def do_get(url):
    try:
        #Perform GET
        print("Connecting to "+url)
        ans = requests.get(url)

        #Verify status ok or else
        if ans.status_code == 200:
            print(f"Response: {ans.text}")
            pass
        else:
            print(f"Connection error: {ans.status_code}")
            print(ans.text)

    except requests.exceptions.Timeout:
        print("Error: Timeout")
    except requests.exceptions.RequestException as e:
        print(f"Bad request: {e}")

#Draws a yellow square around the given pixel
def drawYellowSquare(frame,pixel):
    cv2.rectangle(frame, (pixel[0]-2, pixel[1]-2), (pixel[0]+2,pixel[1]+2), (0,255,255), 2)
    #return frame

def drawRedSquare(frame,pixel):
    cv2.rectangle(frame, (pixel[0]-2, pixel[1]-2), (pixel[0]+2,pixel[1]+2), (0,0,255), 2)
    #return frame

def drawBlueSquare(frame,pixel):
    cv2.rectangle(frame, (pixel[0]-2, pixel[1]-2), (pixel[0]+2,pixel[1]+2), (255,0,0), 2)
    #return frame


base_url="http://192.168.1.13:8000" #Use ip to prevent delay in DNS resolution

video=cv2.VideoCapture(f"{base_url}/video_feed")




# Configura el tamaño del frame (Pi zero)
video.set(3, 320)  # Ancho
video.set(4, 240)  # Alto

# Check if the video opened successfully
if (video.isOpened()== False): 
    print("Error opening video file")
    
#Initial conditions
initial_frame = None
hits=0
detected=False
clear_alarm=True
fresh_frame=False

zero_counter = 0
frame_count = 0

####Main loop
#We start an infinite loop and keep reading frames from the webcam until we press 'q'
while True:
    check, frame = video.read()
    
    #Frame counter
    frame_count += 1
    #print("Frame "+str(frame_count))
    if frame_count==1000:
        frame_count = 0


    #If no frame, then quit
    if check==False:
        print("Video ended")
        break #breaks loop and quits
    

    #Gray conversion and noise reduction (smoothening)
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    #blur_frame=cv2.GaussianBlur(gray_frame,(13,13),0)
    blur_frame=cv2.bilateralFilter(gray_frame,9,75,75)

    
    #The first captured frame is the baseline image
    if initial_frame is None:
        initial_frame = blur_frame
        

    #Lets refresh reference frames every 5seg
    if int(time.time())%5==0 and fresh_frame==False:
        initial_frame = blur_frame
        #print("Forced refresh")
        fresh_frame=True
        



    # The difference between the baseline and the new frame
    delta_frame=cv2.absdiff(initial_frame,blur_frame)
    
    #Let's blur the difference image a bit more to make some features dissapear (holes)
    delta_frame = cv2.GaussianBlur(delta_frame, (3,3), 0)
    
    #Thresholding THRESH_BINARY, THRESH_TOZERO
    threshold_frame=cv2.threshold(delta_frame,10,255, cv2.THRESH_TOZERO)[1]
            
        
    
    #print(hits)
        
        
    
    #If MASK is found, apply it to the frame
    mask = cv2.imread("mask.jpg",cv2.COLOR_BGR2GRAY)
    if mask is None:
        print("Mask failed to load")
        exit()
    #mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    #print("mask "+str(mask.shape))
    else:
    #We apply the mask image to exclude image areas
        result_masked = cv2.multiply(threshold_frame,mask)
    
    #print("result mult "+str(result_mult.shape))
        
        
        


    # The cv2.findContours() method we will identify all the contours in our image.
    # This method expects 3 parameters, (a) image, (b) contour retrieval mode and
    # (c) contour approximation method
    (contours,_)=cv2.findContours(result_masked,cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_NONE)
    
    #Draw all contours
    #cv2.drawContours(frame,contours,-1,(255,0,0),3)
    

    for c in contours:
        # contourArea() method filters out any small contours
        # You can change this value
        if cv2.contourArea(c) > 4000:
            #threading.Thread(target=do_get, args=(f"{base_url}/alarm",)).start()     
            (x, y, w, h)=cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
            #cv2.drawContours(frame,[c],-1,(0,255,0),1)



    #loop through all pixels in the masked image
    """    for row in range(result_masked.shape[0]): 
          
        for col in range(result_masked.shape[1]):
            pix=result_masked[row][col]

            if pix>60 and detected==False:
                hits=hits+1
                print("HIT "+str(pix))
                detected=True
                ##Trigger alarm in own thread
                threading.Thread(target=do_get, args=(f"{base_url}/alarm",)).start()     
                fresh_frame=False
                drawYellowSquare(frame,(col,row)) #draw yellow square around touched pixel
                frame_count=1 #reset frame counter
                clear_alarm=False
            
            else:
                #count 300 frames before resetting detected flag
                if frame_count%72==0 and detected==True:
                    detected=False
                    print("Resetting detected flag")
                    initial_frame = blur_frame #fail to detect slow moving elements
    """

    
    #Show Frames
    cv2.imshow('Main view', frame)
    #cv2.imshow('Baseline (blurred) image', initial_frame)
    #cv2.imshow("Gray Frame",gray_frame)
    #cv2.imshow('Delta frame', delta_frame)   
    #cv2.imshow('Threshold frame', threshold_frame)
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
