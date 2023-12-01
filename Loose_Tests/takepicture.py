import picamera

camera = picamera.PiCamera()

camera.resolution=(320,240)

camera.capture('image.jpg')

camera.close()

print("Image taken")