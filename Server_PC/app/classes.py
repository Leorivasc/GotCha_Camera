import sqlite3
import requests
import datetime
import cv2
import threading
import time
import numpy as np

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


def do_get(url):
    """Perform a GET request to the specified URL.
    Args:
        url (str): The URL to which the request will be performed.
    Returns:
        str: The response text if the request was successful, an error message otherwise.
    """

    try:
        #Perform GET
        print("Connecting to "+url)
        ans = requests.get(url)

        #Verify status ok or else
        if ans.status_code == 200:
            print(f"Response: {ans.text}")
            return(f"{ans.text}")
            pass
        else:
            print(f"Connection error: {ans.status_code}")
            return(f"Connection error: {ans.status_code}")

    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return("Error: Timeout")
    except requests.exceptions.RequestException as e:
        print(f"Bad request: {e}")
        return(f"Bad request: {e}")


def read_config(camera_name):
    """Read the cameras configuration from database by using SQLiteDB class.
    Args:
        camera_name (str): The name of the camera to be read.
    Returns:
        Camera information row as dict.
    """
    connection = SQLiteDB()
    connection.connect()
    camera = connection.query_data_dict("cameras","name='"+camera_name+"'")
    connection.close_connection()
    return camera


def read_config_all():
    """Read all the cameras configuration from database by using SQLiteDB class.
    Returns:
        Camera information rows as dict.
    """
    connection = SQLiteDB()
    connection.connect()
    cameras = connection.query_data_dict("cameras", "isEnabled=1")
    connection.close_connection()
    return cameras


def add_datetime(frame):
    #Get date
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    #Configurar el texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, frame.shape[0] - 10)
    font_scale = 0.5
    font_color = (0, 255, 0)  # Verde
    line_type = 1

    #Put text
    cv2.putText(frame, time, bottom_left_corner, font, font_scale, font_color, line_type)
    return frame




class Three_Frame_Difference:

    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.last_frame = None   #To store the last frame
        self.frame_thread = None #To control the thread from within the function
        self.frame_lock = threading.Lock()
        self.loopOK=True         #To control the restarting of the loop upon desconnection from cammera
        self.foreverLoop=True   #To control the forever loop

    def three_frame_difference_loop(self):

        """This function implements a three-frame difference algorithm to detect movement.
        It uses last_frame to store the last frame so that it is accessible from /video_feed function
        It must be run on its own thread so that it does not block the main thread
        Args:
            camera_name (str): The name of the camera to be used. It must be the registered in the database.sqlite DB.
            At the same time, it must be given as an argument to the -e flag on gunicorn launch command (-e CAMERA=camera_name)

            To run standalone: CAMERA=<camera_name> python3 mov_fr_subs_stream_class.py

        """


        print(f"THREEFRAME Camera: {self.camera_name}")


        #Get camera configuration from DB using the camera name as key
        camera=read_config(self.camera_name)[0] #only the 1st result just in case an error has two cameras with the same name
        
        url = f"http://{camera['ip_address']}:{camera['port']}" #url for the camera stream
        
        #Open the stream
        cap = cv2.VideoCapture(f"{url}/video_feed") 

        #Preload 3 consecutive frames numbered 1, 2, 3 (1st frame is discarded)
        _, frame1 = cap.read()
        _, frame2 = cap.read()
        _, frame3 = cap.read()

        print(f"Starting 3-frame difference algorithm: {self.camera_name}")

        while self.loopOK:

            #Get camera configuration AGAIN from DB so that changes are applied on each iteration LIVE
            camera=read_config(self.camera_name)[0] #only the 1st result just in case

            #Apply camera configuration on each iteration
            N = int(camera['frameskip'])
            detectionarea = int(camera['detectionarea'])

            # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
            frame1 = frame2.copy()
            frame2 = frame3.copy()

            #Read N consecutive frames fo throw away
            for i in range(0, N):
                dropFrames=cap.read() #dropFrames never used

            # Read new 3rd frame
            _, frame3 = cap.read()
            
            #Loop to reconnect if connection is lost. It will loop until a frame is read again
            if not _:
                 # No more frames to read or connection lost?
            #lets loop until we get a frame again
                print("No more frames to read. Connection lost?")
                while not _:
                    time.sleep(5) #Retry in 5 seconds
                    print("Trying to reconnect...")
                    try:
                        cap = cv2.VideoCapture(f"{url}/video_feed") 
                        _, frame3 = cap.read()
                    except:
                        print("Connection failed. Trying again...")
                    finally:
                        if _:
                            print("Connection reestablished")
                            #self.restartLoop()
                            self.loopOK=False
                            break
                            

            #Calculate difference between consecutive frames
            diffA = cv2.absdiff(frame1, frame2)
            diffB = cv2.absdiff(frame2, frame3)

            # Bitwise OR of the 2 frame differences as suggested in paper
            diff = cv2.bitwise_or(diffA, diffB)


            #Convert to grayscale
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # Aplicar un umbral para resaltar las diferencias
            _, threshold_diff = cv2.threshold(gray_diff, 100, 255, cv2.THRESH_BINARY)

            # Dilatar la imagen para rellenar huecos
            threshold_diff = cv2.dilate(threshold_diff, np.ones((3, 3), np.uint8), iterations=2)


            #If MASK is found, apply it to the frame. 'name' must match the camera name
            mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY)
            if mask is None:
                print("Mask not found. Creating default mask")
                image = np.zeros((240,320),dtype=np.uint8)
                #image[:120,:]=1 #Top half of the image is '1', bottom half is '0' (image looks black)
                image[:]=1 #All image is '1' (image looks black)
                cv2.imwrite(f'masks/mask_{self.camera_name}.jpg', image)
                mask = cv2.imread(f"masks/mask_{self.camera_name}.jpg",cv2.COLOR_BGR2GRAY) #Read the mask again
            else:
                
                #We apply the m ask image to exclude image areas with "0" in the mask
                #diff = cv2.bitwise_and(diff,mask)
                threshold_diff = cv2.multiply(threshold_diff,mask) #Works with grayscale images



            # Find contours in the thresholded image
            contours, _ = cv2.findContours(threshold_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
                # contourArea() method filters out any small contours
                # You can change this value
                #print(cv2.contourArea(c))
                if cv2.contourArea(c)> detectionarea: #Sensitive to small movements
                    (x, y, w, h)=cv2.boundingRect(c)
                    cv2.rectangle(frame1, (x, y), (x+w, y+h), (0,0,255), 1) #Red rectangle
                    #print("Movement detected")
                    ###MOVEMENT DETECTION HERE###

                    do_get(f"{url}/alarm") #Send alarm to server

                else:
                    (x, y, w, h)=cv2.boundingRect(c)
                    cv2.rectangle(frame1, (x, y), (x+w, y+h), (125,255,255), 1) #yellow rectangle

            
            with self.frame_lock: 
                self.last_frame = frame1.copy()
                add_datetime(self.last_frame)
            

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
            



class VideoRecorder:
    """This class implements a video recorder. (needs OPENCV)"""

    def __init__(self,url ,fps=12, resX=320, resY=240):
        self.isRecording = False
        self.url=url     
        self.fps=fps
        self.resX=resX
        self.resY=resY

    def save_video_span(self,duration):
        # Init camera
        cap = cv2.VideoCapture(self.url)

        self.isRecording = True

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
            frame = add_datetime(frame)

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
        self.isRecording = False #Recording finished


    def isRecording(self):
        return self.isRecording


