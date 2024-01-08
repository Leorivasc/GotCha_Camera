#Collection of functions used by the main program and the classes


import cv2
import numpy as np
import requests
from .sqlitedb import SQLiteDB
import datetime



def do_get(url):
    """Perform a GET request to the specified URL.
    Args:
        url (str): The URL to which the request will be performed.
    Returns:
        Tuple: True/False, The response text if the request was successful, an error message otherwise.
    """

    try:
        #Perform GET
        #print("Connecting to "+url)
        ans = requests.get(url)

        #Verify status ok or else
        if ans.status_code == 200:
            #print(f"Response: {ans.text}")
            return((True,f"{ans.text}")) #Returns TUPLE (True, response)

        else:
            #print(f"Connection error: {ans.status_code}")
            return((False,f"Connection error: {ans.status_code}"))

    except requests.exceptions.Timeout:
        #print((False,"Error: Timeout"))
        return((False,"Error: Timeout"))
    except requests.exceptions.RequestException as e:
        #print((False,f"Bad request: {e}"))
        return((False,f"Bad request: {e}"))


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


def add_text(frame, text, x,y):
    #Configurar el texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (x,y)
    font_scale = 0.5
    font_color = (0, 255, 0)  # Verde
    line_type = 1

    #Put text
    cv2.putText(frame, text, bottom_left_corner, font, font_scale, font_color, line_type)
    return frame


def createMask(camera_name):
    """Create a mask image for the specified camera name under masks/ directory. With name mask_<camera_name>.jpg"""
    image = np.zeros((240,320),dtype=np.uint8)
    #image[:120,:]=1 #Top half of the image is '1', bottom half is '0' (image looks black)
    image[:]=1 #All image is '1' (image looks black and makes no effect on the analysis)
    cv2.imwrite(f'masks/mask_{camera_name}.jpg', image)
    
def loopUntilRead(cap, url):
    """This function checks the connection to the camera and restarts the loop if connection is lost.
    It must be run on its own thread so that it does not block the main thread
    Args:
        cap (cv2.VideoCapture): The video capture object.
        url (str): The URL to which the request will be performed.
    """
    #Loop to reconnect if connection is lost. It will loop until a frame is read again
    print("Connection lost?")
    _=False

    while not _:
        time.sleep(5) #Retry in 5 seconds
        print("Trying to reconnect...")
        try:
            cap = cv2.VideoCapture(f"{url}/video_feed") 
            _, frame = cap.read()
        except:
            print("Connection failed. Trying again...")
        finally:
            if _:
                print("Connection reestablished")                
                return frame

