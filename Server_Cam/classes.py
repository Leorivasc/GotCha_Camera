import RPi.GPIO as GPIO
import threading
import time
import datetime
import cv2

#This class implements a GPIO output that can be turned on, off or blink
class GPIO_Out:
    #Constructor
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.is_blinking = False
        self.frequency = 0.25  # Default requency in hz
        self.blink_thread = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.turn_off() #Start turned off
        self.status = "OFF"

    #Turns on
    def turn_on(self):
        self._on()
        self.status = "ON"

    def _on(self):
         GPIO.output(self.gpio_pin, GPIO.HIGH)


    #Turn off
    def turn_off(self):
        self._off()
        self.status = "OFF"


    def _off(self):
        GPIO.output(self.gpio_pin, GPIO.LOW)


    #Blinker (don't use directly)
    def _blink(self):
        while self.is_blinking:
            self._on()
            time.sleep(1 / (2 * self.frequency))
            self._off()
            time.sleep(1 / (2 * self.frequency))
            

    #Starts blinking
    def start_blinking(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_thread = threading.Thread(target=self._blink)
            self.blink_thread.start()
            self.status = "BLINKING"

    #Stops blinking
    def stop_blinking(self):
        if self.is_blinking:
            self.is_blinking = False
            self.blink_thread.join()  # Espera a que la thread termine
            self.blink_thread = None
            self.status = "OFF"

    #Set blinker frequency
    def set_frequency(self, frequency):
        self.frequency = frequency
        # If it was blinking, restart with new frequency
        if self.is_blinking:
            self.stop_blinking()
            self.start_blinking()

    #Get blinker frequency
    def get_frequency(self):
        return self.frequency


    #Gets status
    def get_status(self):
        return self.status

    #Free resource
    def cleanup(self):
        GPIO.cleanup()



#this class implements a counter that can be incremented or decremented
class Counter:
    def __init__(self, initial_value=0):
        self.value = initial_value

    def inc(self):
        self.value += 1

    def dec(self):
        self.value -= 1

    def reset(self):
        self.value = 0

    def set(self, value):
        self.value = value

    def get(self):
        return self.value



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


class VideoRecorder:
    """This class implements a video recorder"""



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


        # Libera los recursos
        cap.release()
        video_out.release()
        self.isRecording = False #Recording finished


    def isRecording(self):
        return self.isRecording




class ThingBuffer:
    """This class implements a small buffer with r/w control bit
        Usable inside main loops to keep values unchanged conditionally
    """
    
    def __init__(self, initial_value=None):
        self.value = initial_value
        self.locked = False

    def store(self, value):
        if not self.locked:
            self.value = value #Store value
            self.locked = True #Lock buffer until cleared
            return True
        else:
            #print("Buffer is locked. Can't store value.")
            return False

    def get(self):
        return self.value
    
    def lock(self):
        self.locked = True   

    def unlock(self):
        self.locked = False


