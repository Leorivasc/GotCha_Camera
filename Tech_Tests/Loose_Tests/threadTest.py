from flask import Flask
import threading
import time

app = Flask(__name__)
a=0

def background_task():
    global a
   
    # Esta función se ejecutará en segundo plano
    while True:
        a+=1
        print("Ejecutando tarea en segundo plano..."+str(a))
        
        #sleep 1 second
        time.sleep(1)

        # Agrega aquí la lógica de tu tarea en segundo plano
        # Puedes usar time.sleep() para evitar un uso excesivo de la CPU

# Crear un hilo para ejecutar la función en segundo plano
background_thread = threading.Thread(target=background_task)
background_thread.start()

# Rutas y lógica de tu aplicación Flask
@app.route('/')
def index():
    return '¡Hola, mundo!'

# Iniciar la aplicación Flask
if __name__ == '__main__':

    if not background_thread.is_alive():
        background_thread.start()

    app.run(debug=False, threaded=True)
