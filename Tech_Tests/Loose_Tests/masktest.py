#Creates a mask and applies it to an image
#Basically a demo of how to use a mask on a picture

import cv2
import numpy as np

# Cargar la imagen
img = cv2.imread('superamigues.jpg')

# Crear una máscara binaria del mismo tamaño que la imagen
mask = np.zeros_like(img)

# Definir los vértices del polígono que representa el área a excluir
vertices = np.array([[100, 100], [200, 100], [200, 200], [100, 200]])

# Rellenar el polígono en la máscara con blanco
cv2.fillPoly(mask, [vertices], (255, 255, 255))

# Aplicar la máscara a la imagen
img_masked = cv2.bitwise_and(img, mask)

# Mostrar la imagen enmascarada
cv2.imshow('Image', img_masked)
cv2.waitKey(0)
cv2.destroyAllWindows()
