import RPi.GPIO as GPIO
import threading
import time

class GPIO_Out:
    #Constructor
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.is_blinking = False
        self.frequency = 0.5  # Default requency in hz
        self.blink_thread = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.turn_off() #Start turned off

    #Turns on
    def turn_on(self):
        GPIO.output(self.gpio_pin, GPIO.HIGH)

    #Turn off
    def turn_off(self):
        GPIO.output(self.gpio_pin, GPIO.LOW)

    #Blinker (don't use directly)
    def _blink(self):
        while self.is_blinking:
            self.turn_on()
            time.sleep(1 / (2 * self.frequency))
            self.turn_off()
            time.sleep(1 / (2 * self.frequency))

    #Starts blinking
    def start_blinking(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_thread = threading.Thread(target=self._blink)
            self.blink_thread.start()

    #Stops blinking
    def stop_blinking(self):
        if self.is_blinking:
            self.is_blinking = False
            self.blink_thread.join()  # Espera a que la thread termine
            self.blink_thread = None

    #Set blinker frequency
    def set_frequency(self, frequency):
        self.frequency = frequency
        # If it was blinking, restart with new frequency
        if self.is_blinking:
            self.stop_blinking()
            self.start_blinking()

    #Free resource
    def cleanup(self):
        GPIO.cleanup()
