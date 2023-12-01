import cv2
from threading import Thread
from queue import Queue

class RaspberryPiCamera:
    def __init__(self, ip, port):
        self.url = f'http://{ip}:{port}/video_feed'
        self.window_name = f'Raspberry Pi Camera ({ip})'
        self.cap = cv2.VideoCapture(self.url)
        self.frame_queue = Queue()
        self.is_running = True

    def start(self):
        # Inicia un hilo para obtener el video
        thread = Thread(target=self.get_video)
        thread.start()
        return thread

    def get_video(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Pone el frame en la cola
            self.frame_queue.put(frame)

        self.cap.release()

    def show_video(self):
        while True:
            # Obtiene el frame de la cola
            frame = self.frame_queue.get()

            # Muestra el frame en la ventana
            cv2.imshow(self.window_name, frame)

            # Espera 1 ms y verifica si se ha presionado la tecla 'q'
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                self.is_running = False
                break

        cv2.destroyAllWindows()

# Lista de cámaras con sus respectivas IP y puertos
cameras = [
    RaspberryPiCamera(ip='192.168.1.14', port=5000),
    RaspberryPiCamera(ip='192.168.1.17', port=5000)
    # Añade más cámaras si es necesario
]

# Inicia un hilo para cada cámara
threads = [camera.start() for camera in cameras]

# Inicia un hilo para mostrar el video
show_thread = Thread(target=lambda: [camera.show_video() for camera in cameras])
show_thread.start()

# Espera a que todos los hilos terminen
for thread in threads:
    thread.join()

# Espera a que el hilo de mostrar video termine
show_thread.join()
