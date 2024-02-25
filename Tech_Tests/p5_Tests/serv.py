from flask import Flask, render_template, Response
from flask_cors import CORS
from threading import Thread
from queue import Queue
from camera import RaspberryPiCamera
import cv2


app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Rutas de ejemplo para los streams de cámaras
@app.route('/stream1')
def stream1():
    # Lógica para obtener el stream de la cámara 1
    # Reemplaza este código con la lógica real para obtener el stream
    return Response(get_camera_stream("http://192.168.1.17:5000/video_feed"), content_type='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream2')
def stream2():
    # Lógica para obtener el stream de la cámara 2
    # Reemplaza este código con la lógica real para obtener el stream
    return Response(get_camera_stream("http://direccion_ip_2:puerto/stream"), content_type='multipart/x-mixed-replace; boundary=frame')

# Función de ejemplo para obtener el stream de la cámara
def get_camera_stream(camera_url):
    # Implementa la lógica para obtener el stream aquí
    # Por ejemplo, puedes usar OpenCV para obtener el stream de la cámara



# Resto de la configuración del servidor Flask...
if __name__ == '__main__':
    app.run(debug=True)
