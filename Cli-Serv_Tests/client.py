#Simple client to test the server. It will display the video feed from the server
#It will not do any processing on the frames

import cv2

url = 'http://192.168.1.17:5000/video_feed'

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()

    if ret==False:
        print("Could not get image. Server down or busy")
        break

    # Tu lógica de procesamiento aquí

    try:
        cv2.imshow('Live Video', frame)
    except:
        pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

