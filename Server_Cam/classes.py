## Useul classes for the server_cam project

import RPi.GPIO as GPIO
import threading
import time
import datetime


#This class implements a GPIO output that can be turned on, off or blink
class GPIO_Out:
    #Constructor
    def __init__(self, gpio_pin):
        '''Initializes the GPIO pin as output and turned off.
        Args:
            gpio_pin (int): The GPIO pin number to be used.
        '''
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
        '''Turns on the GPIO pin using _on() method.'''
        self._on()
        self.status = "ON"



    def _on(self):
        '''Turns on the GPIO pin.'''
        GPIO.output(self.gpio_pin, GPIO.HIGH)




    #Turn off
    def turn_off(self):
        '''Turns off the GPIO pin using _off() method.'''
        self._off()
        self.status = "OFF"



    def _off(self):
        GPIO.output(self.gpio_pin, GPIO.LOW)




    #Blinker (don't use directly)
    def _blink(self):
        '''Blinking thread. Don't use directly. Use start_blinking() instead.
        '''

        while self.is_blinking:
            self._on()
            time.sleep(1 / (2 * self.frequency))
            self._off()
            time.sleep(1 / (2 * self.frequency))




    #Starts blinking (use this)
    def start_blinking(self):
        '''Starts blinking the GPIO pin using _blink() method in a thread.
        '''

        if not self.is_blinking:
            self.is_blinking = True
            self.blink_thread = threading.Thread(target=self._blink)
            self.blink_thread.start()
            self.status = "BLINKING"




    #Stops blinking
    def stop_blinking(self):
        '''Stops blinking the GPIO pin.
        '''

        if self.is_blinking:
            self.is_blinking = False
            self.blink_thread.join()  # Espera a que la thread termine
            self.blink_thread = None
            self.status = "OFF"




    #Set blinker frequency
    def set_frequency(self, frequency):
        '''Sets the frequency of the blinker.
        Args:
            frequency (float): The frequency in hz.
        '''

        self.frequency = frequency
        # If it was blinking, restart with new frequency
        if self.is_blinking:
            self.stop_blinking()
            self.start_blinking()




    #Get blinker frequency
    def get_frequency(self):
        '''Gets the frequency of the blinker.
        Returns:
            float: The frequency in hz.
        '''
        return self.frequency





    #Gets status
    def get_status(self):
        '''Gets the status of the GPIO pin.
        Returns:
            str: The status of the GPIO pin.
        '''
        return self.status




    #Free resource
    def cleanup(self):
        '''Cleans up the GPIO pin.
        '''
        GPIO.cleanup()





#--------------------------------------------------------------------------------
#this class implements a counter that can be incremented or decremented
#Good for use inside 'while true' loops and change values conditionally
class Counter:
    '''This class implements a counter that can be incremented or decremented.'''
    def __init__(self, initial_value=0):
        self.value = initial_value


    def inc(self):
        '''Increments the counter by 1.'''
        self.value += 1


    def dec(self):
        '''Decrements the counter by 1.'''
        self.value -= 1


    def reset(self):
        '''Resets the counter to 0.'''
        self.value = 0


    def set(self, value):
        '''Sets the counter to a specific value.'''
        self.value = value


    def get(self):
        '''Gets the counter value.'''
        return self.value





#--------------------------------------------------------------------------------
#This class implements a timer that calls a function after a certain time
#Useful for waiting a certain time before doing something or keeping a certain state for a while
#(Alert mode, for example)
def wait_timer(seconds, callback, *arg):
    '''This function waits for a certain time and then calls a function.
    Args:
        seconds (float): The time to wait in seconds.
        callback (function): The function to call.
        *arg: The arguments to pass to the function.
    '''
    def timer_thread():
        time.sleep(seconds)
        callback(*arg)

    thread = threading.Thread(target=timer_thread)
    thread.start()




#Class for a small buffer with r/w control bit
class ThingBuffer:
    """This class implements a small buffer with r/w control bit
        Usable inside main loops to keep values unchanged conditionally
    """
    
    def __init__(self, initial_value=None):
        self.value = initial_value
        self.locked = False


    def store(self, value):
        '''Stores a value in the buffer if it's not locked.
        Args:
            value: The value to store.
        Returns:
            bool: True if the value was stored, False if the buffer was locked.
        '''
        if not self.locked:
            self.value = value #Store value
            self.locked = True #Lock buffer until cleared
            return True
        else:
            #print("Buffer is locked. Can't store value.")
            return False

    def get(self):
        '''Gets the value from the buffer.'''
        return self.value
    
    def lock(self):
        '''Locks the buffer.'''
        self.locked = True   

    def unlock(self):
        '''Unlocks the buffer.'''
        self.locked = False


