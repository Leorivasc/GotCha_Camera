#Camera class. To use by importing. Window.

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
            #self.frame_queue.put(frame)
            

            #frame = self.frame_queue.get()

            # Muestra el frame en la ventana
            cv2.imshow(self.window_name, frame)
            # Espera 1 ms y verifica si se ha presionado la tecla 'q'
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                self.is_running = False
                break
            
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

