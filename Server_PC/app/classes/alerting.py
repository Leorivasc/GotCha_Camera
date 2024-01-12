from . import functions as fn
import threading
import time
import json


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

        self.camera_conf = fn.read_config(self.camera_name)[0] #Refresh configuration from DB (in case it has changed)
        
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
