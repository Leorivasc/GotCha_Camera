import RPi.GPIO as GPIO
import threading
import time

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