import cv2

# Capturar video desde la cámara (puedes cambiar el número según tu configuración)
cap = cv2.VideoCapture("http://192.168.1.13:8000/video_feed")

# Inicializar el objeto para el sustractor de fondo
fgbg = cv2.createBackgroundSubtractorMOG2()
while True:
    # Leer un frame del video
    ret, frame = cap.read()
    if ret == False:
        break

    # Aplicar el sustractor de fondo para obtener la máscara de movimiento
    fgmask = fgbg.apply(frame)

    # Aplicar un umbral a la máscara para obtener la región de movimiento
    threshold = 250
    _, thresh = cv2.threshold(fgmask, threshold, 255, cv2.THRESH_BINARY)

    # Encontrar contornos en la región de movimiento
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        # contourArea() method filters out any small contours
        # You can change this value
        if cv2.contourArea(c)> 7000:
            (x, y, w, h)=cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)




    # Dibujar los contornos en el frame original
    #cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

    # Mostrar el frame con la detección de movimiento
    cv2.imshow('Motion Detection', frame)
    #cv2.imshow('Mask', fgmask)
    cv2.imshow('Treshold', thresh)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()
