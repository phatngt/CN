import cv2
import numpy as np
import keyboard
vid = cv2.VideoCapture(0)
while True:
    ret,frame = vid.read()
    cv2.imshow('frame',frame)
    fr = cv2.imencode('.JPEG',frame)
    print(fr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()