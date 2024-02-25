#FLASK APP. Standalone.Serves video streaming. 
#Receives mask image and saves it in upload folder

from flask import Flask, render_template, Response, request,send_from_directory
from werkzeug.utils import secure_filename
import os

import cv2

app = Flask(__name__)
cap = cv2.VideoCapture(0)
####PC CAMERA REFUSES TO CHANGE RESOLUTION USING cap.set()####
cap.set(3, 320)  # Ancho
cap.set(4, 240)  # Altura

#uploading mask image config
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

success, sampleframe = cap.read()
if not success:
    print("Error reading from camera")
else:
    file_path = f'upload/frame.jpg'
    cv2.imwrite(file_path, sampleframe)


#Frames for video feed
def generate_frames():
    while True:
        try:
            # Lee un cuadro de la cámara
            success, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) ## Correct color for cv2, or else it looks blue
            ##16:9=640,360
            frame = cv2.resize(frame, (320, 240)) ####FORCE RESIZE (pc camera refuses to change resolution using cap.set())
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error reading from camera or color correcting, will pass... {e}")
            pass

#Route for video
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')





# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ruta para cargar la página inicial
@app.route('/')
def index():
    return render_template('index.html')

   

# Ruta para servir archivos estáticos (HTML, JS, CSS, imágenes, etc.)
@app.route('/mask_app/<path:filename>')
def serve_static(filename):
    return send_from_directory('mask_app', filename)




# Ruta para manejar la carga de archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificar si se ha enviado un archivo
    if 'mask' not in request.files:
        return 'No se ha enviado ningún archivo'

    file = request.files['mask']

    # Verificar si el nombre del archivo está vacío
    if file.filename == '':
        return 'Nombre de archivo vacío'

    # Verificar si la extensión del archivo es permitida
    if file and allowed_file(file.filename):
        # Asegurar el nombre del archivo y guardarlo en la carpeta de carga
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'Archivo subido con éxito'

    return 'Extensión de archivo no permitida'




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

