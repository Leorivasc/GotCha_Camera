#Will record video from given camera.
#Rough onthe edges, but it works.


import cv2

# Inicializa la cámara
cap = cv2.VideoCapture("http://192.168.1.23:5000/video_feed")

# Verifica si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error al abrir la cámara.")
    exit()

# Configura la grabación de video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 6
video_salida = cv2.VideoWriter('video_salida.avi', fourcc, fps, (320, 240))  # Ajusta el tamaño según sea necesario

# Graba la secuencia de video durante 10 segundos
tiempo_inicial = cv2.getTickCount()
while True:
    ret, frame = cap.read()

    if not ret:
        print("Error al capturar el fotograma.")
        break

    # Graba el fotograma en el video de salida
    video_salida.write(frame)

    # Muestra el fotograma en una ventana (opcional)
    cv2.imshow('Video', frame)

    # Sale del bucle después de 10 segundos
    tiempo_actual = cv2.getTickCount()
    tiempo_transcurrido = (tiempo_actual - tiempo_inicial) / cv2.getTickFrequency()
    if tiempo_transcurrido > 60:
        break

    # Sale del bucle cuando se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera los recursos
cap.release()
video_salida.release()
cv2.destroyAllWindows()
