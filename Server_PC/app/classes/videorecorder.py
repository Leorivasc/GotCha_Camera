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
        self.video_out = None

        self.tempfilename = f"{self.camera_name}_alert.webm"
        self.recording = False
        
        #Get the path to the database file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        self.destfolder = os.path.join(thisfolder, '..', 'recordings')

    def startRecording(self):
        self.recording = True
        if self.date == None:
            self.date = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
            self.filename=f"alarm_{self.camera_name}_{self.date}.webm" #Set filename
            self.iniTicks = cv2.getTickCount() #Set initial time
            #self.video_out = cv2.VideoWriter(self.tempfilename, cv2.VideoWriter_fourcc(*'XVID'), 12, (320,240))  # Resolution
            self.video_out = cv2.VideoWriter(self.tempfilename, cv2.VideoWriter_fourcc(*'VP90'), 12, (320,240))
            print(f"Recording {self.camera_name}")


    def recordFrame(self, frame, timespan):

        self.timespan = timespan
        #time.sleep(0.083) #12fps      

        #Print datetime on frame
        frame = fn.add_datetime(frame)

        #Record frame
        self.video_out.write(frame)

        #Breaks after 'duration' seconds
        current_time = cv2.getTickCount()
        time_passed = (current_time - self.iniTicks) / cv2.getTickFrequency()
        #print(time_passed) #DEBUG
        if time_passed > self.timespan:
            self.stopRecording()
            return
        else:
            self.recording = True



    def stopRecording(self):
        self.video_out.release()
        self.recording = False
        self.date = None
        #rename file
        os.rename(self.tempfilename, self.filename)
        print(f"Recording finished {self.camera_name}")

    def isRecording(self):
        return self.recording
    
    
    def _justRecord(self,url,timespan):
        #Will roughly record timespan seconds of video on its own routine. Not using other functions
        #use this function on its own thread

        self.url=url

        #Init camera
        cap = cv2.VideoCapture(f"{self.url}{self.camera_config['path']}")
        #Verify cam opening
        if not cap.isOpened():
            print("Error opening camera.")
            exit()

        #Configure video recording
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fourcc = cv2.VideoWriter_fourcc(*'VP90')
        video_out = cv2.VideoWriter(f'alarm_{self.camera_name}.webm', fourcc, 12, (320,240))

        newname=f"alarm_{self.camera_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.webm"

        #Graba la secuencia de video durante 10 segundos
        ini_time = cv2.getTickCount()

        #Recording loop
        while True:

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
        os.rename(f"alarm_{self.camera_name}.webm", os.path.join(self.destfolder,newname))

    def justRecord(self,url,timespan):
        if self.recording:
            print("Busy recording")
            return
        print(f"Recording {self.camera_name}, {timespan} seconds")
        self.recording = True
        thread = threading.Thread(target=self._justRecord, args=(url,timespan,))
        thread.start()

