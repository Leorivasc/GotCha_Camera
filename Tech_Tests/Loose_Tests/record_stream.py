#Tries to record a stream from the camera, taking advantage of the same frame currently being displayed on the screen.
# Usa el loop principal
# Inicia o detiene la grabación al presionar 'R'

import cv2
import time

# Inicializar la cámara (reemplaza con la configuración de tu cámara)
camera = cv2.VideoCapture("http://pizero1.local:8000/video_feed")

# Variables para controlar la grabación
grabando = False
inicio_grabacion = 0
duracion_grabacion = 5  # en segundos
nombre_archivo = 'grabacion.avi'

# Inicializar VideoWriter cuando se inicia la grabación
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None

# Bucle principal
while True:
    ret, frame = camera.read()
    cv2.imshow('Video', frame)

    key = cv2.waitKey(1) & 0xFF

    # Iniciar o detener la grabación al presionar 'R'
    if key == ord('R') or key == ord('r'):
        if not grabando:
            grabando = True
            inicio_grabacion = time.time()
            out = cv2.VideoWriter(nombre_archivo, fourcc, 24, (320, 240))
        else:
            grabando = False
            out.release()

    # Grabar el frame si la grabación está activa
    if grabando:
        out.write(frame)

    # Detener grabación después de N segundos
    if grabando and time.time() - inicio_grabacion > duracion_grabacion:
        grabando = False
        out.release()

    # Salir al presionar 'q'
    if key == ord('q'):
        break

# Liberar recursos y cerrar ventanas
camera.release()
cv2.destroyAllWindows()
