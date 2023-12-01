# Build A Motion Detected Alarm System with Python

# let’s import the libraries
# For playing the audio, we will be using “pyttsx3” python library to convert text to speech
import cv2
import pyttsx3
import threading
import time


# This funtion plays the audio message
def voice_alarm(alarm_sound):
    alarm_sound.say("alert")
    alarm_sound.runAndWait()
    

# Setting parameters for voice
alarm_sound = pyttsx3.init()
voices = alarm_sound.getProperty('voices')
alarm_sound.setProperty('voice', voices[0].id)
alarm_sound.setProperty('rate', 150)


# The function to play the audio wil be executed in a separate thread.
# So, there won't be lag in the video feed while the audio alert message is playing.
alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,))


#status_list=[None,None]
status_list=[0,0]
initial_frame = None


# We use VideoCapture function to create the video capture object
video=cv2.VideoCapture(0)


# Configura el tamaño del frame (Pi zero)
video.set(3, 640)  # Ancho
video.set(4, 480)  # Alto




# We start an infinite loop and keep reading frames from the webcam until we press 'q'
while True:
    check, frame = video.read()
    status=0

    # Gray conversion and noise reduction (smoothening)
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur_frame=cv2.GaussianBlur(gray_frame,(25,25),0)

    
    # The first captured frame is the baseline image
    if initial_frame is None:
        initial_frame = blur_frame
        continue

    # The difference between the baseline and the new frame
    delta_frame=cv2.absdiff(initial_frame,blur_frame)
    # The difference (the delta_frame) is converted into a binary image
    # If a particular pixel value is greater than a certain threshold (specified by us here as 150),
    # it will be assigned the value for White (255) else Black(0)
    # Important: you may have to change the threshold value for a better performance with your webcam , room's light, etc.
    threshold_frame=cv2.threshold(delta_frame,150,255, cv2.THRESH_BINARY)[1]
    

    # The cv2.findContours() method we will identify all the contours in our image.
    # This method expects 3 parameters, (a) image, (b) contour retrieval mode and
    # (c) contour approximation method
    (contours,_)=cv2.findContours(threshold_frame,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        # contourArea() method filters out any small contours
        # You can change this value
        if cv2.contourArea(c) < 1000:
            continue
        status=status + 1
        (x, y, w, h)=cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
    status_list.append(status)


    # The alarm is triggered if an 'intruder' is detected
    # We can also trigger the alarm only if a moving object is detected with
    #if status_list[-1]>= 1 and status_list[-2]==0:    
    if status_list[-2]>= 1:
        if (alarm.is_alive() == False):
            alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,))
            alarm.start()

        
    # To better understand the application, we can visualise the different frames generated
    cv2.imshow('Webcam', frame)
    cv2.imshow('Baseline image', initial_frame)
    #cv2.imshow("Gray Frame",gray_frame)
    #cv2.imshow('Delta frame', delta_frame)   
    cv2.imshow('Threshold frame', threshold_frame)
    

    # Stop the program by pressing 'q'    
    if cv2.waitKey(1) == ord('q'):
        break

        
# After the loop release the video object, stop the alarm
# and destroy all the windows
alarm_sound.stop()
video.release()
cv2.destroyAllWindows()
