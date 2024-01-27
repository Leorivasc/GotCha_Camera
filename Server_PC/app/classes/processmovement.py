##THIS WILL IMPORT A MOVEMENT DETECTION CLASS FROM A SEPARATE FILE AND USE IT##

import cv2
import numpy as np
import threading
import time
from . import functions as fn
from .alerting import Alerting
from .videorecorder import VideoRecorder
from .threeframe import ThreeFrame
import json

class ProcessMovement:

    def __init__(self, camera_name, recorder_obj, processedrecorder_obj, alert_obj):
        self.camera_name = camera_name
        self.last_frame = None   #To store the last frame
        self.frame_thread = None #To control the thread from within the function
        self.frame_lock = threading.Lock()
        self.loopOK=True         #To control the restarting of the loop upon desconnection from cammera
        #self.foreverLoop=True   #To control the forever loop
       
        self.camera_conf = fn.read_config(self.camera_name)[0] #Get camera configuration from DB using the camera name as key
        #self.url = f"http://{self.camera_conf['ip_address']}:{self.camera_conf['port']}" #url for the camera


        #self.alerting= Alerting(self.camera_name) #Instantiate alerting handler object
        self.alerting= alert_obj #Reuses the alerting object from the main script
        #self.videoRecorder = VideoRecorder(self.camera_name) #Instantiate video recorder object
        self.videoRecorder = recorder_obj #Reuses the recorder object from the main script
        #self.processedRecorder = VideoRecorder(self.camera_name,"Processed_") #Instantiate video recorder object for processed video
        self.processedRecorder = processedrecorder_obj #Reuses the recorder object from the main script



    def main_loop(self):



        #Get camera configuration from DB using the camera name as key
        camera=fn.read_config(self.camera_name)[0] #only the 1st result just in case an error has two cameras with the same name
        self.camera_conf=camera #Save camera configuration to object attribute
        
        self.url = f"http://{camera['ip_address']}:{camera['port']}{camera['path']}" #url for the camera stream
        

        #Open the stream
        cap = cv2.VideoCapture(self.url) 
        #cap.set(cv2.CAP_PROP_BUFFERSIZE, 12) #Set buffer size to 12 frames

        #Initialize the 3-frame difference algorithm
        threeframe = ThreeFrame(cap,self.url)

        while self.loopOK:

            #Get camera configuration AGAIN from DB so that changes are applied on each iteration LIVE
            #Depending on cpu speed (Pi server?) it may fail due to DB lock during config changes
            try:
                camera=fn.read_config(self.camera_name)[0] #only the 1st result just in case
            except:
                print("Error reading camera configuration from DB. We keep previous configuration until next iteration")


            #Apply camera configuration on each iteration. 
            N = int(camera['frameskip'])
            detectionarea = int(camera['detectionarea'])

            #Update detection threshold
            threeframe.setDetectionThreshold(int(camera['detectionthreshold']))
            
            #Skip frames
            for i in range(N):
                cap.grab()


            #----Obtain the resulting frames from 3-frame difference algorithm----#
            #Get the 3-frame difference image (binary and dilated), the diff and the last frame
            diff, threshold_diff, currentframe = threeframe.processFrame() 




            #----Masking areas on image----#
            #We apply a mask to the image to exclude areas that are not of interest
            #This is useful to exclude areas that are always moving (like trees or flags or pedestrians)

            #This is achieved by multiplying the mask image by the threshold_diff image (1 or 0)
            #The mask image must be the same size as the threshold_diff image
            #The mask image must be grayscale (1 channel)
            
            #If MASK is found, apply it to the frame. 'name' must match the camera name
            mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY)
            if mask is None:
                #If not found, create a default mask
                print("Mask not found. Creating default mask")
                fn.createMask(self.camera_name) #Create default null mask (filled with '1')
                mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY) #Read the mask again
                

            #We apply the mask image to exclude image areas with "0" in the mask
            #diff = cv2.bitwise_and(diff,mask)
            try:    
                #This operation fails on uploaded images because of the 3rd dimension in the mask
                threshold_diff = cv2.multiply(threshold_diff,mask) #Works with grayscale images
            except:
                #Remove 3rd dimension from mask and retry
                mask=mask[:,:,0] #If mask is RGB, convert to grayscale
                threshold_diff = cv2.multiply(threshold_diff,mask) #Retry



            #----Detecting contours----#

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(threshold_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #Save last frame before drawing rectangles
            #if self.videoRecorder.isRecording():
            #    self.videoRecorder.recordFrame(frame1, timespan=self.camera_conf['recordtime'])

            # Loop over the contours (THERE COULD BE MANY EACH FRAME)
            for c in contours:

                #locate c coords and size
                (x, y, w, h)=cv2.boundingRect(c)

                if cv2.contourArea(c)> detectionarea: #Sensitive to small movements
                    
                    cv2.rectangle(currentframe, (x, y), (x+w, y+h), (0,0,255), 1) #Red rectangle
                    
                    if not self.alerting.isAlerting() and camera['isTriggerable'] == 1:
                        self.alerting.startAlert() #Start alerting system
                    #self.videoRecorder.startRecording() #Start recording

                    if not self.videoRecorder.isRecording():
                        self.videoRecorder.recordTimeLapse(camera['recordtime']) #Start recording on its own thread
                        
                        #Record processed images only if configured
                        if camera['recordProcessed'] == 1:
                            time.sleep(1) #Wait for the recording to start before starting the processed recording
                            print("Recording processed video")
                            self.processedRecorder.recordProcessedTimeLapse(camera['recordtime']) #Start recording on its own thread

                    continue #We don't want to trigger the alert again if there are more detections in this frame

                else:
                    cv2.rectangle(currentframe, (x, y), (x+w, y+h), (125,255,255), 1) #yellow rectangle
                    pass

                #add box size
                #frame1 = add_text(frame1,str(cv2.contourArea(c)),x+2,y+2) #Print contour number on frame

            with self.frame_lock: 
                self.last_frame = currentframe.copy()
                fn.add_datetime(self.last_frame)
            

            
        cap.release()

        #if self.foreverLoop:
        #    self.restartLoop() 



    def startLoop(self):
        """Start the three-frame difference loop on a new thread."""


        if self.frame_thread is None:
            self.frame_thread = threading.Thread(target=self.main_loop)
            self.loopOK=True
            #self.foreverLoop=True
            self.frame_thread.start()
            
            #self.frame_thread.join() #HANGS LOOP

        
        else:
            print("Thread already running")
            


    def stopLoop(self):
        """Stop the three-frame difference loop."""
        self.loopOK=False
        #self.frame_thread.join()
        self.frame_thread = None   


    def restartLoop(self):
        """Restart the three-frame difference loop."""
        self.stopLoop()
        time.sleep(3)
        print("Restarting loop")
        self.startLoop()


    def generate_frames(self):
        while True:
            with self.frame_lock:
                if self.last_frame is None:
                    continue

                #We sleep to reduce network traffic. If not present, there is always an image to yield
                #then traffic may reach 1.5 to 2MB/s and hang the browser (firefox in particular)
                time.sleep(0.083) #12fps (limits traffic to ~300KB/s)

                #Convert to jpeg,then bytes, then send
                _, buffer = cv2.imencode('.jpg', self.last_frame)
                frame_bytes = buffer.tobytes()

            #Yield the frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + f"{len(frame_bytes)}".encode() + b'\r\n'
                    b'\r\n' + frame_bytes + b'\r\n')    


    def getSnapshot(self):
        """Return the last frame as a JPEG image."""
        with self.frame_lock:
            if self.last_frame is None:
                return None

            _, buffer = cv2.imencode('.jpg', self.last_frame)
            frame_bytes = buffer.tobytes()

        return frame_bytes
    
    def getState(self):
        """Return the object state."""
        return self.loopOK

    def getStateXX(self):
        """Return the object state."""
        response = {"loopOK": self.loopOK, "isRecording": self.videoRecorder.isRecording(),"isProcessedrecording": self.processedRecorder.isRecording(),"isAlerting": self.alerting.isAlerting()}
        responseJSON = json.dumps(response)
        return responseJSON