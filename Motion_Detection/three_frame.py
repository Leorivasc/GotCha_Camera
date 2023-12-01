#MALO

# Importamos las bibliotecas necesarias
import cv2
import numpy as np

# Cargamos el vídeo
cap = cv2.VideoCapture("video_salida.avi")
cap.set(3, 320)  # Ancho
cap.set(4, 240)  # Alto

while cap.isOpened():
    # Leemos los tres primeros fotogramas
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    ret, frame3 = cap.read()

    # Convertimos los fotogramas a escala de grises
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)

    # Inicializamos el fondo con el primer fotograma
    background = gray1


    # Calculamos la diferencia absoluta entre los fotogramas
    diff1 = cv2.absdiff(gray1, gray2)
    diff2 = cv2.absdiff(gray2, gray3)
    
    # Sumamos las dos diferencias
    motion_diff = cv2.add(diff1, diff2)
    
    # Calculamos la diferencia absoluta entre el fotograma actual y el fondo
    background_diff = cv2.absdiff(gray3, background)
    
    # Actualizamos el fondo
    background = gray3
    
    # Combinamos las dos imágenes binarias
    combined_diff = cv2.bitwise_or(motion_diff, background_diff)
    
    # Mostramos la imagen resultante
    cv2.imshow('Deteccion de movimiento', combined_diff)
    
    cv2.imshow("cualqiera",diff1)

    # Leemos el siguiente fotograma
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convertimos el fotograma a escala de grises
    gray1 = gray2
    gray2 = gray3
    gray3 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Liberamos los recursos y cerramos las ventanas
cap.release()
cv2.destroyAllWindows()
