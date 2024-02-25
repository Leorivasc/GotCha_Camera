from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return os.getenv('MENSAJE')

if __name__ == '__main__':
    mensaje=os.getenv('MENSAJE')
    print(mensaje)
    app.run(host='0.0.0.0', port=8000)


### Cargar con:
### MENSAJE="MENSAJE DE TEXTO" gunicorn -w 4 -b 0.0.0.0:8000 app:app
### o gunicorn -w 1 -b 0.0.0.0:8000 test_args:app -e MENSAJE="MENSAJE DE TEXTO"
### 
### y acceder a http://localhost:8000