import cv2
from threading import Thread

class RaspberryPiCamera:
    def __init__(self, ip, port):
        self.url = f'http://{ip}:{port}/video_feed'
        self.window_name = f'Raspberry Pi Camera ({ip})'
        self.cap = cv2.VideoCapture(self.url)

    def start(self):
        # Inicia un hilo para obtener y mostrar el video
        thread = Thread(target=self.get_and_show_video)
        thread.start()
        return thread

    def get_and_show_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            
            cv2.imshow(self.window_name, frame)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

        self.cap.release()
        cv2.destroyAllWindows()

# Lista de cámaras con sus respectivas IP y puertos
cameras = [
    RaspberryPiCamera(ip='192.168.1.14', port=5000),
    RaspberryPiCamera(ip='192.168.1.17', port=5000)
    # Añade más cámaras si es necesario
]

# Inicia un hilo para cada cámara
threads = [camera.start() for camera in cameras]

# Espera a que todos los hilos terminen
for thread in threads:
    thread.join()

