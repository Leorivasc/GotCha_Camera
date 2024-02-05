from . import functions as fn
import threading
import time
import json
from .emailsender import EmailSender


class Alerting:
    """This class implements an alerting system handler."""

    def __init__(self, camera_name, app, recorder_obj):
        self.camera_name = camera_name
        self.camera_conf = fn.read_config(self.camera_name)[0] #Get camera configuration from DB using the camera name as key
        self.url = f"http://{self.camera_conf['ip_address']}:{self.camera_conf['port']}" #url for the camera stream
        self.isalerting = False
        self.recorder_obj = recorder_obj
        self.body = ""

        #Create an email sender object, notice that the app context and the recorder object are passed to the email sender
        self.email = EmailSender(app) 

    def _run_timer(self, seconds, callback, *arg):
        self.isalerting = True
        def timer_thread():
            time.sleep(seconds)
            self.isalerting = False
            callback(*arg)

        thread = threading.Thread(target=timer_thread)
        thread.start()




    def startAlert(self, seconds=None):

        self.camera_conf = fn.read_config(self.camera_name)[0] #Refresh configuration from DB (in case it has changed)
        
        #To allow triggering a different alert length than the camera default
        if seconds is None:
            seconds = self.camera_conf['alertlength']

        conn_ok, alertstatus = fn.do_get(f"{self.url}/status")
        alertstatus=json.loads(alertstatus) #Reads JSON status from camera

        #print(f"StartAlert() ALERTSTATUS:{alertstatus['alert']}") #Debug

        #If camera is connected and alert is not active, send alarm
        if conn_ok and alertstatus['alert'] == "False":
                self.body = f"Movement detected in camera {self.camera_conf['name']}. Sending alarm. {str(seconds)} seconds"
                print(self.body)
                fn.do_get(f"{self.url}/alarm") #Send alarm to camera

                self._run_timer(seconds, self.stopAlert) #Start timer to stop alarm
        else:
            print(f"Already alerting..{self.camera_conf['name']}")
            
    

    def stopAlert(self):
        conn_ok, alertstatus = fn.do_get(f"{self.url}/status")
        alertstatus=json.loads(alertstatus) #Reads JSON status from camera
        
        #print(f"StopAlert() ALERTSTATUS:{alertstatus['alert']}") #Debug

        #Send email. At this point, video and thumbnail are already saved
        self.body = self.body + f" Last image: {self.recorder_obj.getLastThumbnailName()}"
        print (self.body)
        self.email.send(self.camera_conf['emailAlert'], "Security Alert", self.body)

        #If camera is connected and alert is active, STOP alarm
        if conn_ok: #and alertstatus['alert'] == "True":
                print(f"Stopping alarm in camera {self.camera_conf['name']}.")
                fn.do_get(f"{self.url}/clear")
        else:
            print("Alarm already inactive")
        

    def isAlerting(self):
        return self.isalerting
