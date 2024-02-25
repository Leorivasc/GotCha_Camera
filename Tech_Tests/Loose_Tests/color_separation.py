# Python program to explain Merging of Channels 

# Importing cv2 
import cv2 

# Reading the BGR image using imread() function 
image = cv2.imread("superamigues.jpg") 

# Splitting the channels first to generate different 
# single 

# channels for merging as we don't have separate 
# channel images 
r, g, b = cv2.split(image) 

# Displaying Blue channel image 
cv2.imshow("Model Blue Image", b) 

# Displaying Green channel image 
cv2.imshow("Model Green Image", g) 

# Displaying Red channel image 
cv2.imshow("Model Red Image", r) 

avg = (r+g+b)/3
cv2.imshow("AVG", avg) 

# Using cv2.merge() to merge Red, Green, Blue Channels 
# into a coloured/multi-channeled image 
image_merge = cv2.merge([r, g, b]) 

# Displaying Merged RGB image 
cv2.imshow("RGB_Image", image_merge) 

# Waits for user to press any key 
cv2.waitKey(0) 
