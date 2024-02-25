# Capture and display webcam with Python and OpenCV

import cv2

# We use VideoCapture function to create the video capture object
# Note we put '0' to capture webcam
video=cv2.VideoCapture(0)

# We start an infinite loop and keep reading frames from the webcam until we press 'q'
while True:
    check, frame = video.read()
    cv2.imshow("Webcam",frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# After the loop release the video object
video.release()

# Destroy all the windows
cv2.destroyAllWindows()
