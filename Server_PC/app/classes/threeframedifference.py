import cv2
import numpy as np
import threading
import time
from . import functions as fn
from .alerting import Alerting
from .videorecorder import VideoRecorder



class Three_Frame_Difference:

    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.last_frame = None   #To store the last frame
        self.frame_thread = None #To control the thread from within the function
        self.frame_lock = threading.Lock()
        self.loopOK=True         #To control the restarting of the loop upon desconnection from cammera
        self.foreverLoop=True   #To control the forever loop
       
        self.camera_conf = fn.read_config(self.camera_name)[0] #Get camera configuration from DB using the camera name as key
        self.url = f"http://{self.camera_conf['ip_address']}:{self.camera_conf['port']}" #url for the camera stream


        self.alerting= Alerting(self.camera_name) #Instantiate alerting handler object
        self.videoRecorder = VideoRecorder(self.camera_name) #Instantiate video recorder object
        #self.savideorecorder = StandaloneVideoRecorder(self.url) #Instantiate standalone video recorder object


    def three_frame_difference_loop(self):

        """This function implements a three-frame difference algorithm to detect movement.
        It uses last_frame to store the last frame so that it is accessible from /video_feed function
        It must be run on its own thread so that it does not block the main thread
        """


        print(f"THREEFRAME Camera: {self.camera_name}")


        #Get camera configuration from DB using the camera name as key
        camera=fn.read_config(self.camera_name)[0] #only the 1st result just in case an error has two cameras with the same name
        self.camera_conf=camera #Save camera configuration to object attribute
        
        self.url = f"http://{camera['ip_address']}:{camera['port']}" #url for the camera stream
        

        #Open the stream
        cap = cv2.VideoCapture(f"{self.url}/video_feed") 

        #Preload 3 consecutive frames numbered 1, 2, 3 (1st frame is discarded)
        _, frame1 = cap.read()
        _, frame2 = cap.read()
        _, frame3 = cap.read()

        print(f"Starting 3-frame difference algorithm: {self.camera_name}")

        while self.loopOK:

            #Get camera configuration AGAIN from DB so that changes are applied on each iteration LIVE
            camera=fn.read_config(self.camera_name)[0] #only the 1st result just in case

            #Apply camera configuration on each iteration. 
            N = int(camera['frameskip'])
            detectionarea = int(camera['detectionarea'])
            detectionthreshold = int(camera['detectionthreshold'])

            # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
            frame1 = frame2.copy()
            frame2 = frame3.copy()

            #Read N consecutive frames fo throw away to work only with the Nth frame
            for i in range(0, N):
                cap.read() #void read

            # Read new 3rd frame
            read, frame3 = cap.read()
            
            #Loop to reconnect if connection is lost. It will loop until a frame is read again
            #cap dies if connection is lost. loopUntilRead() will loop until a frame is read again
            #and return a new cap object and a new frame to resume the loop
            while read==False:
                 (read,frame3,cap)=fn.loopUntilRead(cap,self.url) #Reconnect and return frame. Should hang in here until frame is read again
                            

            #Calculate difference between consecutive frames
            diffA = cv2.absdiff(frame1, frame2)
            diffB = cv2.absdiff(frame2, frame3)

            # Bitwise OR of the 2 frame differences as suggested in paper (Srivastav, 2017)
            diff = cv2.bitwise_or(diffA, diffB)


            #Convert to grayscale
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # Apply threshold to enhance differences
            _, threshold_diff = cv2.threshold(gray_diff, detectionthreshold, 255, cv2.THRESH_BINARY)

            # Dilate to fill in holes
            threshold_diff = cv2.dilate(threshold_diff, np.ones((5, 5), np.uint8), iterations=2)


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
                    
                    cv2.rectangle(frame1, (x, y), (x+w, y+h), (0,0,255), 1) #Red rectangle
                    
                    if not self.alerting.isAlerting() and self.camera_conf['isTriggerable'] == 1:
                        self.alerting.startAlert() #Start alerting system
                    #self.videoRecorder.startRecording() #Start recording

                    if not self.videoRecorder.isRecording():
                        self.videoRecorder.recordTimeLapse(self.camera_conf['recordtime']) #Start recording on its own thread

                    continue #We don't want to trigger the alert again if there are more detections in this frame

                else:
                    cv2.rectangle(frame1, (x, y), (x+w, y+h), (125,255,255), 1) #yellow rectangle

                #add box size
                #frame1 = add_text(frame1,str(cv2.contourArea(c)),x+2,y+2) #Print contour number on frame

            with self.frame_lock: 
                self.last_frame = frame1.copy()
                fn.add_datetime(self.last_frame)
            

            
        cap.release()

        if self.foreverLoop:
            self.restartLoop() 



    def startLoop(self):
        """Start the three-frame difference loop on a new thread."""


        if self.frame_thread is None:
            self.frame_thread = threading.Thread(target=self.three_frame_difference_loop)
            self.loopOK=True
            self.foreverLoop=True
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

                # Convertir el frame a formato JPEG para la transmisión web
                _, buffer = cv2.imencode('.jpg', self.last_frame)
                frame_bytes = buffer.tobytes()

    
            #yield (b'--frame\r\n'
            #      b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + f"{len(frame_bytes)}".encode() + b'\r\n'
                    b'\r\n' + frame_bytes + b'\r\n')    


    def snapshot(self):
        """Return the last frame as a JPEG image."""
        with self.frame_lock:
            if self.last_frame is None:
                return None

            _, buffer = cv2.imencode('.jpg', self.last_frame)
            frame_bytes = buffer.tobytes()

        return frame_bytes