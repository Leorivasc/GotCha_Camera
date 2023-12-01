import threading
import pygame.mixer as mixer

def reproducir_mp3(nombre_archivo):
    # Inicializa el mezclador de audio de pygame
    mixer.init()

    # Crea un objeto de sonido
    sonido = mixer.Sound(nombre_archivo)

    # Reproduce el sonido en una hebra separada
    def reproducir():
        sonido.play()

    # Crea una hebra para reproducir el sonido
    hilo_reproduccion = threading.Thread(target=reproducir)

    # Inicia la hebra
    hilo_reproduccion.start()

# Uso de la función para reproducir un archivo MP3
archivo_mp3 = 'ejemplo.mp3'  # Reemplaza con la ruta de tu archivo MP3
reproducir_mp3(archivo_mp3)

