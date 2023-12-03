#Crea una imagen mitad '1' y mitad '0'. Para usar *multiplicando* otra imagen

import numpy as np
import cv2

image = np.zeros((480,640),dtype=np.uint8) ## rows, cols (height, width)
image[:120,:]=1 #Ojo es 1, muy parecido al negro. Blanco es 255

cv2.imwrite('mask.jpg', image)

