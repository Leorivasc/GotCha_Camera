#Collection of functions used by the main program and the classes


import cv2
import numpy as np
import requests
from .sqlitedb import SQLiteDB
import datetime
import time
import hashlib


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


    camera=None
    while camera is None:
        try:
            camera = connection.query_data_dict("cameras","name='"+camera_name+"'")
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)

            
    return camera

def read_email_config():
    """Read the email configuration from database by using SQLiteDB class.
    Returns:
        Email information row as dict.
    """
    connection = SQLiteDB()

    email=None
    while email is None:
        try:
            email = connection.query_data_dict("email", "id=1") #There is only one row in the email table
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)

    return email

def read_config_all(condition=None):
    """Read all the cameras configuration from database by using SQLiteDB class.
    Returns:
        Camera information rows as dict.
    """
    connection = SQLiteDB()

    cameras=None

    while cameras is None:
        try:
            cameras = connection.query_data_dict("cameras", condition)
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)
    

    return cameras

def update_email_config(data):
    """Update the email configuration from database by using SQLiteDB class.
    Args:
        data (dict): The data to be updated.
    Returns:
        True if the update was successful, False otherwise.
    """
    connection = SQLiteDB()

    ans=False

    tries=0
    while ans is False and tries<5: ##Will try 5 times before giving up
        try:
            ans = connection.update_data("email", data, "id=1") #There is only one row in the email table
        except Exception as e:
            #If the database is locked, wait 1 second and try again
            print("Error updating. Waiting 1 second...")
            time.sleep(1)
            
    

    return ans

def read_users():
    """Read all the users from database by using SQLiteDB class.
    Returns:
        Users information rows as dict.
    """
    connection = SQLiteDB()

    users=None

    while users is None:
        try:
            users = connection.query_data_dict("users")
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)
    

    return users

def is_user(username):
    """Check if the specified user exists in the database by using SQLiteDB class.
    Args:
        username (str): The name of the user to be checked.
    Returns:
        True if the user exists, False otherwise.
    """
    connection = SQLiteDB()

    user=None

    while user is None:
        try:
            user = connection.query_data_dict("users","username='"+username+"' LIMIT 1")
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)
    

    if user == []:
        return False
    else:
        return True


def get_pass(username):
    """Read the password of the specified user from database by using SQLiteDB class.
    Args:
        username (str): The name of the user to be read.
    Returns:
        User information row as dict.
    """
    connection = SQLiteDB()

    user=None

    while user is None:
        try:
            user = connection.query_data_dict("users","username='"+username+"'")
        except:
            #If the database is locked, wait 1 second and try again
            print("Database locked. Waiting 1 second...")
            time.sleep(1)
    

    return user

def update_config(camera_name, data):
    """Update a row given the camera name and the data to be updated.
    Notice that NAME is used as key to reference cameras, but whenever CAMERA NAME
    is modified, we must use the id to reference the camera (w2ui grid specially)

    Args:
        camera_name (str): The name of the camera to be updated.
        data (dict): The data to be updated.
    Returns:
        True if the update was successful, False otherwise.
    """
    connection = SQLiteDB()

    ans=False
    condition = "" #To be sent to the update_data function

    #Whenever camera name is modified, we can't use it as condition, we must use the id
    
    if data.get('id') is not None:
        condition = "id='"+str(data['id'])+"'"
        del data['id'] #Remove any operation on the id column
    else:
        condition = "name="+"'"+camera_name+"'"


    tries=0
    while ans is False and tries<5: ##Will try 5 times before giving up
        try:
            ans = connection.update_data("cameras", data, condition)
        except Exception as e:
            #If the database is locked, wait 1 second and try again
            print("Error updating. Waiting 1 second...")
            time.sleep(1)
            
    

    return ans


def new_camera(data):
    connection = SQLiteDB()

    #Insert the camera
    id = connection.insert_data("cameras", data)

    #Update the camera name with mirror port 5000+id
    connection.update_data("cameras", {"mirrorport":5000+id}, "id="+str(id))

    return id

def remove_camera(camera_name):
    connection = SQLiteDB()

    #Delete the camera by name
    ans = connection.delete_data("cameras", "name='"+camera_name+"'")

    return ans

def add_datetime(frame):
    #Get date
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    #Configurar el texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, frame.shape[0] - 10)
    font_scale = 0.5
    font_color = (11, 127, 217)  # Orange
    line_type = 1

    #Put text
    cv2.putText(frame, time, bottom_left_corner, font, font_scale, (0,0,0), 3) #Shadow
    cv2.putText(frame, time, bottom_left_corner, font, font_scale, font_color, line_type)
    return frame


def add_text(frame, text, x,y):
    #Configurar el texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (x,y)
    font_scale = 0.5
    font_color = (11, 127, 217)  # Orange
    line_type = 1

    #Put text
    cv2.putText(frame, text, bottom_left_corner, font, font_scale, (0,0,0), 3) #Shadow
    cv2.putText(frame, text, bottom_left_corner, font, font_scale, font_color, line_type)
    return frame


def createMask(camera_name):
    """Create a mask image for the specified camera name under masks/ directory. With name mask_<camera_name>.jpg"""
    image = np.zeros((240,320),dtype=np.uint8)
    #image[:120,:]=1 #Top half of the image is '1', bottom half is '0' (image looks black)
    image[:]=1 #All image is '1' (image looks black and makes no effect on the analysis)
    cv2.imwrite(f'masks/mask_{camera_name}.jpg', image)
    
def loopUntilRead(cap,url):
    """This function checks the connection to the camera and restarts the loop if connection is lost.
    It must be run on its own thread so that it does not block the main thread
    Args:
        cap (cv2.VideoCapture): The video capture object.
        url (str): The URL to which the request will be performed.
    """
    #Loop to reconnect if connection is lost. It will loop until a frame is read again
    print(f"Connection lost to {url}.")
    _=False

    while not _:
        time.sleep(5) #Retry in 5 seconds
        print("Trying to reconnect...")
        try:
            cap.release()
            cap = cv2.VideoCapture(f"{url}") 
            _, frame = cap.read()
        except:
            print("Connection failed. Trying again...")
        finally:
            if _:
                print("Connection reestablished")                
                return (True,frame,cap)


# Credit: https://stackoverflow.com/questions/5297448/how-to-get-md5-sum-of-a-string-using-python
def md5hash(string):
    '''Return the md5 hash of the string'''

    return hashlib.md5(string.encode('utf-8')).hexdigest()

