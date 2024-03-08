import cv2
import datetime
import os
import threading
from . import functions as fn
import time
import socket

class VideoRecorder:
    """This class implements a video recorder object.
    It is used to record time-lapse videos from the camera stream.
    It also handles the creation of thumbnails and the storage of the videos in the filesystem.
    """
    
    def __init__(self, cameraName, processName=""):
        self.cameraName = cameraName
        self.processName = processName
        self.cameraConfig = fn.read_config(cameraName)[0]
        self.date = None
        self.iniTicks = None
        self.videofilename = "DEFAULT.WEBM"
        self.thumbnailname = "DEFAULT.PNG"
        self.video_out = None

        self.tempfilename = ""
        self.recording = False
        
        #Get the path to the database file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        self.destfolder = os.path.join(thisfolder, '..', 'recordings')
        self.url = f"http://{self.cameraConfig['ip_address']}:{self.cameraConfig['port']}"

    
    def _recordTimeLapseWEBM(self,url,timespan):
        '''This method records a time-lapse video from the camera stream.
        It uses the OpenCV library to capture the frames and store them in a webm file.
        The video is stored in the filesystem and a thumbnail is created.
        Better used from a thread to avoid blocking the main process.
        
        Args:
            url (str): The URL of the camera stream.
            timespan (int): The duration of the video in seconds.

        Returns:
            None. It will save the video and the thumbnail in the filesystem.
        '''

        #Note about codecs:
        #vp90 seem to work but accelerates video (misses frames?)
        #vp80 seems to work ok, even in the PI

        self.url=url
        #self.tempfilename = f"{self.cameraName}_alert.webm"

        #Init camera
        cap = cv2.VideoCapture(f"{self.url}{self.cameraConfig['path']}")
        #Verify cam opening
        if not cap.isOpened():
            print("Error opening camera.")
            return

        #Configure video recording
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fourcc = cv2.VideoWriter_fourcc(*'vp80')
        
        self.videofilename=f"{self.processName}{self.cameraName}_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.webm"
        self.thumbnailname=self.videofilename.replace(".webm",".jpg")

        video_out = cv2.VideoWriter(self.videofilename, fourcc, 12, (320,240))

        
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
            frame = fn.add_text(frame,self.cameraName,10,20)

            #Record frame
            video_out.write(frame)

            #Breaks after 'duration' seconds
            current_time = cv2.getTickCount()
            time_passed = (current_time - ini_time) / cv2.getTickFrequency()
            #print(time_passed) #DEBUG
            if time_passed > timespan:
                self.recording = False #Recording finished

        #Free resources
        cap.release()
        video_out.release()
        print("Recording finished")
        
         #create thumbnail
        self.createThumbnail(self.videofilename, self.thumbnailname)
        #Move files to dest folder
        os.rename(self.videofilename, os.path.join(self.destfolder,self.videofilename)) 
        os.rename(self.thumbnailname, os.path.join(self.destfolder,self.thumbnailname)) 




    def recordTimeLapse(self,timespan):
        '''This method records a time-lapse video from the camera stream.
        It triggers a thread with the _recordTimeLapseWEBM method.
        
        Args:
            timespan (int): The duration of the video in seconds.
            
        Returns:
            None. It will start a recorder thread with the provided timespan.'''
        
        if self.recording:
            print("Busy recording")
            return
        print(f"Recording {self.cameraName}, {timespan} seconds")
        self.recording = True
        thread = threading.Thread(target=self._recordTimeLapseWEBM, args=(self.url,timespan,))
        thread.start()



    def recordProcessedTimeLapse(self,timespan):
        '''This method records a time-lapse video from the processed camera stream.
        It triggers a thread with the _recordTimeLapseWEBM method but using the processed stream instead of the raw stream.
        
        Args:
            timespan (int): The duration of the video in seconds.
            
        Returns:
            None. It will start a recorder thread with the provided timespan.'''

        if self.recording:
            print("Busy recording")
            return
        print(f"Recording {self.cameraName}, {timespan} seconds")
        self.recording = True

        host_name = socket.gethostname()+".local" #.local is needed to avoid having 127.0.0.1 as address (not used)
        #host_name = socket.getfqdn()
        server_ip = socket.gethostbyname(host_name)
        #This is the LOCAL result of the processed video (the one with the bounding boxes)
        processedurl = f"http://{server_ip}:{self.cameraConfig['mirrorport']}"
        print(processedurl)
        thread = threading.Thread(target=self._recordTimeLapseWEBM, args=(processedurl,timespan,))
        thread.start()




    def isRecording(self):
        '''Returns the recording status.'''
        return self.recording
    



    def stopRecording(self):
        '''Stops the recording loop.'''

        #This will break the recording loop
        self.recording = False
        print("Stopping recording")




    def startRecording(self):
        '''Just record a very long video until stopRecording is called'''
        self.recordTimeLapse(1000000)




    def createThumbnail(self, src, dest_file):
        '''Creates a thumbnail from a video file.
        Args:
            src (str): The source video file.
            dest_file (str): The destination thumbnail file.
        Returns:
            None. It will save the thumbnail in the filesystem.'''
        
        cap = cv2.VideoCapture(src)
        success, image = cap.read()
        if success:
            cv2.imwrite(dest_file, image)
        cap.release()



    def getLastThumbnailName(self):
        '''Returns the last thumbnail created'''
        return self.thumbnailname
    



    def getLastVideoName(self):
        '''Returns the last video created'''
        return self.videofilename
    


    def getLastThumbnailPath(self):
        '''Absolute path to the last thumbnail (to prevent the '..' in the path)'''
        return os.path.abspath(os.path.join(self.destfolder,self.thumbnailname))
    