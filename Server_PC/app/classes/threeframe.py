## Description: Class to handle the three frame difference method for motion detection

import cv2
import numpy as np
from . import functions as fn


class ThreeFrame:


    # Constructor
    def __init__(self, cap, url):
        '''Constructor for the ThreeFrame class.
        Args:
            cap (cv2.VideoCapture): The capture device to read frames from.
            url (str): The URL of the capture device.
        Returns:
            Object: The ThreeFrame object.
            '''
        self.cap = cap
        self.url = url
        self.detectionthreshold = 30
        self.classname = "ThreeFrame"

        _, self.frame1 = self.cap.read()
        _, self.frame2 = self.cap.read()
        _, self.frame3 = self.cap.read()
        
        print(f"ThreeFrame object created ({self.url})")
        


    # Process frame
    def processFrame(self):
        '''Process a frame using the three frame difference method.
        Args:
            None
        Returns:
            tuple: A tuple containing the difference image, thresholded difference image, and the current frame.'''

        # Renumber 2nd frame as 1st, 3rd frame as 2nd, and load new frame as 3rd
        self.frame1 = self.frame2.copy()
        self.frame2 = self.frame3.copy()

        # Read new 3rd frame
        read, self.frame3 = self.cap.read()

        #Patch for when the camera is disconnected.
        #Reconnect and return frame. Should hang in here until frame is read again
        while read==False:
            (read,self.frame3,self.cap)=fn.loopUntilRead(self.cap,self.url) 
            
             
        #Calculate difference between consecutive frames
        diffA = cv2.absdiff(self.frame1, self.frame2)
        diffB = cv2.absdiff(self.frame2, self.frame3)

        # Bitwise OR of the 2 frame differences as suggested in paper (Srivastav, 2017)
        diff = cv2.bitwise_or(diffA, diffB)


        #Convert to grayscale
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Apply threshold to enhance differences
        _, threshold_diff = cv2.threshold(gray_diff, self.detectionthreshold, 255, cv2.THRESH_BINARY)

        # Dilate to fill in holes
        threshold_diff = cv2.dilate(threshold_diff, np.ones((5, 5), np.uint8), iterations=2)

        #Returs copy or else it will return a reference to the object and it will be modified with the yellow-red boxes
        return (diff, threshold_diff, self.frame3.copy()) 
    


    # Getters

    def getClassname(self):
        '''Get the class name.  
        Args:
            None
        Returns:
            str: The class name.'''
        
        return self.classname



    def getLastFrame(self):
        '''Get the last frame read from the capture device.
        Args:
            None
        Returns:
            np.array: The last frame read from the capture device.'''
        
        return self.frame3
    


    # Setters
        
    def setCaptureDevice(self, cap):
        '''Set the capture device.
        Args:
            cap (cv2.VideoCapture): The capture device to read frames from. 
        Returns:
            None
        '''
        
        self.cap = cap


    # Set detection threshold
    def setDetectionThreshold(self, threshold):
        '''Set the detection threshold.
        Args:
            threshold (int): The detection threshold.   
        Returns:
            None
        '''
        
        self.detectionthreshold = threshold



    # Read frame
    def readFrame(self):
        '''Read a frame from the capture device.
        Args:
            None
        Returns:
            Tuple: A tuple containing a boolean indicating if the frame was read successfully and the read frame.'''

        read, self.frame3 = self.cap.read() #debug here
        return read, self.frame3
    