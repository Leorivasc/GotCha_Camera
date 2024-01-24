import cv2
import datetime
import os
import threading
from . import functions as fn
import time

class VideoRecorder:
    
    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.camera_config = fn.read_config(camera_name)[0]
        self.date = None
        self.iniTicks = None
        self.filename = None
        self.thumbnailname = None
        self.video_out = None

        self.tempfilename = ""
        self.recording = False
        
        #Get the path to the database file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        self.destfolder = os.path.join(thisfolder, '..', 'recordings')
        self.url = f"http://{self.camera_config['ip_address']}:{self.camera_config['port']}"

    
    def _recordTimeLapseWEBM(self,url,timespan):
        #vp90 seem to work but accelerates video
        #vp80 seems to work ok

        self.url=url
        #self.tempfilename = f"{self.camera_name}_alert.webm"

        #Init camera
        cap = cv2.VideoCapture(f"{self.url}{self.camera_config['path']}")
        #Verify cam opening
        if not cap.isOpened():
            print("Error opening camera.")
            return

        #Configure video recording
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fourcc = cv2.VideoWriter_fourcc(*'vp80')
        
        self.filename=f"{self.camera_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.webm"
        self.thumbnailname=self.filename.replace(".webm",".jpg")

        video_out = cv2.VideoWriter(self.filename, fourcc, 12, (320,240))

        
        #Graba la secuencia de video durante 10 segundos
        ini_time = cv2.getTickCount()

        #Recording loop
        while self.recording:

            time.sleep(0.083) #12fps
            #Read frame
            ret, frame = cap.read()

            if not ret:
                print("Error capturing frame.")
                break

            #Print datetime on frame
            frame = fn.add_datetime(frame)
            frame = fn.add_text(frame,self.camera_name,10,20)

            #Record frame
            video_out.write(frame)

            #Breaks after 'duration' seconds
            current_time = cv2.getTickCount()
            time_passed = (current_time - ini_time) / cv2.getTickFrequency()
            #print(time_passed) #DEBUG
            if time_passed > timespan:
                break

        #Free resources
        cap.release()
        video_out.release()
        print("Recording finished")
        self.recording = False #Recording finished
         #create thumbnail
        self.createThumbnail(self.filename, self.thumbnailname)
        #Move files to dest folder
        os.rename(self.filename, os.path.join(self.destfolder,self.filename)) 
        os.rename(self.thumbnailname, os.path.join(self.destfolder,self.thumbnailname)) 


    def recordTimeLapse(self,timespan):
        if self.recording:
            print("Busy recording")
            return
        print(f"Recording {self.camera_name}, {timespan} seconds")
        self.recording = True
        thread = threading.Thread(target=self._recordTimeLapseWEBM, args=(self.url,timespan,))
        thread.start()



    def isRecording(self):
        return self.recording
    
    def stopRecording(self):
        #This will break the recording loop
        self.recording = False
        print("Stopping recording")

    def startRecording(self):
        #Just record a very long video until stopRecording is called
        self.recordTimeLapse(1000000)

    def createThumbnail(self, src, dest_file):
        cap = cv2.VideoCapture(src)
        success, image = cap.read()
        if success:
            cv2.imwrite(dest_file, image)
        cap.release()