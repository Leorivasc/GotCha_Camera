##### THIS IS A CLASS ONLY VERSION #####

import cv2
import numpy as np
from . import functions as fn

class ThreeFrame:

    def __init__(self, cap, url):
        self.cap = cap
        self.url = url
        self.detectionthreshold = 30
        self.classname = "ThreeFrame"

        _, self.frame1 = self.cap.read()
        _, self.frame2 = self.cap.read()
        _, self.frame3 = self.cap.read()
        

        print(f"ThreeFrame object created ({self.url})")
        
    def processFrame(self):

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
    

    def getClassname(self):
        return self.classname

    def getLastFrame(self):
        return self.frame3
    
    def readFrame(self):
        read, self.frame3 = self.cap.read()
        return read, self.frame3
    
    def setCaptureDevice(self, cap):
        self.cap = cap

    def setDetectionThreshold(self, threshold):
        self.detectionthreshold = threshold