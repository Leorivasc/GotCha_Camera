import sqlite3
import datetime
import cv2
import threading
import time
import numpy as np
import json
import os
import functions as fn




class SQLiteDB:
    """##Generic## SQLite database class.
    Attributes:
        db_name (str): The name of the database file.
        connection (sqlite3.Connection): The database connection object.
        cursor (sqlite3.Cursor): The database cursor object.
    """
    def __init__(self, db_name="database.sqlite"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    #Connect to DB file
    def connect(self): 
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    #Create table (str table_name, str comma separated column names)
    def create_table(self, table_name, columns):      
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(query)
        self.connection.commit()

    #Insert data
    def insert_data(self, table_name, data):
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(query, data)
        self.connection.commit()

    #Query data
    def query_data(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}" #optional

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result


    #Query data as dict
    def query_data_dict(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        cursor = self.cursor

        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            self.connection.close()
            return result


    #Close connection
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()


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

            # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
            frame1 = frame2.copy()
            frame2 = frame3.copy()

            #Read N consecutive frames fo throw away to work only with the Nth frame
            for i in range(0, N):
                cap.read() #void read

            # Read new 3rd frame
            read, frame3 = cap.read()
            
            #Loop to reconnect if connection is lost. It will loop until a frame is read again
            if not read:
                 frame3=fn.loopUntilRead(cap, self.url) #Reconnect and return frame. Should hang in here until frame is read again
                            

            #Calculate difference between consecutive frames
            diffA = cv2.absdiff(frame1, frame2)
            diffB = cv2.absdiff(frame2, frame3)

            # Bitwise OR of the 2 frame differences as suggested in paper (Srivastav, 2017)
            diff = cv2.bitwise_or(diffA, diffB)


            #Convert to grayscale
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # Apply threshold to enhance differences
            _, threshold_diff = cv2.threshold(gray_diff, 100, 255, cv2.THRESH_BINARY)

            # Dilate to fill in holes
            threshold_diff = cv2.dilate(threshold_diff, np.ones((5, 5), np.uint8), iterations=2)


            #If MASK is found, apply it to the frame. 'name' must match the camera name
            mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY)
            if mask is None:
                print("Mask not found. Creating default mask")
                fn.createMask(self.camera_name) #Create default null mask (filled with '1')
                mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY) #Read the mask again
                

            #We apply the m ask image to exclude image areas with "0" in the mask
            #diff = cv2.bitwise_and(diff,mask)
            threshold_diff = cv2.multiply(threshold_diff,mask) #Works with grayscale images



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
                        self.videoRecorder.justRecord(self.url, self.camera_conf['recordtime']) #Start recording on its own thread

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
                
                #time.sleep(0.083) #12fps (limits traffic to ~300KB/s)

                # Convertir el frame a formato JPEG para la transmisión web
                _, buffer = cv2.imencode('.jpg', self.last_frame)
                frame_bytes = buffer.tobytes()

    
            #yield (b'--frame\r\n'
            #      b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + f"{len(frame_bytes)}".encode() + b'\r\n'
                    b'\r\n' + frame_bytes + b'\r\n')    



class Alerting:
    """This class implements an alerting system handler."""

    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.camera_conf = fn.read_config(self.camera_name)[0] #Get camera configuration from DB using the camera name as key
        self.url = f"http://{self.camera_conf['ip_address']}:{self.camera_conf['port']}" #url for the camera stream
        self.isalerting = False
     
    def _run_timer(self, seconds, callback, *arg):
        self.isalerting = True
        def timer_thread():
            time.sleep(seconds)
            self.isalerting = False
            callback(*arg)

        thread = threading.Thread(target=timer_thread)
        thread.start()



    def startAlert(self):
        conn_ok, alertstatus = fn.do_get(f"{self.url}/status")
        alertstatus=json.loads(alertstatus) #Reads JSON status from camera

        #If camera is connected and alert is not active, send alarm
        if conn_ok and alertstatus['alert'] == "False":
                print(f"Movement detected in camera {self.camera_conf['name']}. Sending alarm. {str(self.camera_conf['alertlength'])} seconds")
                fn.do_get(f"{self.url}/alarm") #Send alarm to camera
                self._run_timer(self.camera_conf['alertlength'], self.stopAlert) #Start timer to stop alarm
        else:
            #print("Movement detected but alarm already active")
            pass
    

    def stopAlert(self):
        conn_ok, alertstatus = fn.do_get(f"{self.url}/status")
        alertstatus=json.loads(alertstatus) #Reads JSON status from camera

        #If camera is connected and alert is active, STOP alarm
        if conn_ok and alertstatus['alert'] == "True":
                print(f"Stopping alarm in camera {self.camera_conf['name']}.")
                fn.do_get(f"{self.url}/clear")
        else:
            print("Alarm already inactive")


    def isAlerting(self):
        return self.isalerting

class VideoRecorder:
    
    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.date = None
        self.iniTicks = None
        self.filename = None
        self.video_out = None

        self.tempfilename = f"{self.camera_name}_alert.avi"
        self.recording = False
        

    def startRecording(self):
        self.recording = True
        if self.date == None:
            self.date = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
            self.filename=f"alarm_{self.camera_name}_{self.date}.avi" #Set filename
            self.iniTicks = cv2.getTickCount() #Set initial time
            self.video_out = cv2.VideoWriter(self.tempfilename, cv2.VideoWriter_fourcc(*'XVID'), 12, (320,240))  # Resolution
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
        cap = cv2.VideoCapture(f"{self.url}/video_feed")

        #Verify cam opening
        if not cap.isOpened():
            print("Error opening camera.")
            exit()

        #Configure video recording
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_out = cv2.VideoWriter(f'alarm_{self.camera_name}.avi', fourcc, 12, (320,240))

        newname=f"alarm_{self.camera_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.avi"

        #Graba la secuencia de video durante 10 segundos
        ini_time = cv2.getTickCount()

        #Recording loop
        while True:

            #Read frame
            ret, frame = cap.read()

            if not ret:
                print("Error capturing frame.")
                break

            #Print datetime on frame
            frame = fn.add_datetime(frame)

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
        os.rename(f"alarm_{self.camera_name}.avi", newname)

    def justRecord(self,url,timespan):
        if self.recording:
            print("Busy recording")
            return
        print(f"Recording {self.camera_name}, {timespan} seconds")
        self.recording = True
        thread = threading.Thread(target=self._justRecord, args=(url,timespan,))
        thread.start()


#Not used
class StandaloneVideoRecorder:
    """This class implements a standalone video recorder. (needs OPENCV)"""

    def __init__(self,url ,fps=12, resX=320, resY=240):
        self.isrecording = False
        self.url=url     
        self.fps=fps
        self.resX=resX
        self.resY=resY

    def _save_video_span(self,duration):
        # Init camera
        cap = cv2.VideoCapture(self.url)

        self.isrecording = True

        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d_%H_%M_%S")

        # Verify cam opening
        if not cap.isOpened():
            print("Error opening camera.")
            exit()

        # Configure video recording
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_out = cv2.VideoWriter(f'alarm_{time}.avi', fourcc, self.fps, (self.resX,self.resY))  # Resolution

        # Graba la secuencia de video durante 10 segundos
        ini_time = cv2.getTickCount()

        #Recording loop
        while True:

            #Read frame
            ret, frame = cap.read()

            if not ret:
                print("Error capturing frame.")
                break

            #Print datetime on frame
            frame = fn.add_datetime(frame)

            #Record frame
            video_out.write(frame)

            #Opens in window
            #cv2.imshow('Video', frame)

            #Breaks after 'duration' seconds
            current_time = cv2.getTickCount()
            time_passed = (current_time - ini_time) / cv2.getTickFrequency()
            #print(time_passed) #DEBUG
            if time_passed > duration:
                break #Breaks recording loop


        #Free resources
        cap.release()
        video_out.release()
        self.isrecording = False #Recording finished


    def save_video_thread(self,duration):
        thread = threading.Thread(target=self._save_video_span, args=(duration,))
        thread.start()

    def isRecording(self):
        return self.isrecording
