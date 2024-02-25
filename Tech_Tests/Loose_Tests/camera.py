import cv2

# Inicializa la cámara de la Raspberry Pi
cap = cv2.VideoCapture(0)  # El argumento 0 indica que se usará la primera cámara (la cámara principal)

# Verifica si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error al abrir la cámara.")
    exit()

# Configura el tamaño del frame
cap.set(3, 320)  # Ancho
cap.set(4, 240)  # Alto

# Bucle principal para capturar y mostrar el video en tiempo real
while True:
    # Captura un frame de la cámara
    ret, frame = cap.read()

    # Verifica si se pudo capturar el frame
    if not ret:
        print("Error al capturar el frame.")
        break

    # Muestra el frame en una ventana
    cv2.imshow('Video de la Raspberry Pi', frame)

    # Sale del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la cámara y cierra la ventana
cap.release()
cv2.destroyAllWindows()

