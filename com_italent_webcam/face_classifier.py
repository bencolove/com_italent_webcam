import cv2 as cv
import os
from collections import Iterable

class FaceClassifier:
    def __init__(self, cascade_file='haarcascade_frontalface_default.xml'):
        path = os.path.join(os.getcwd(), 'com_italent_webcam', 'data',cascade_file)
        print(path)
        self._cascade = cv.CascadeClassifier(path)

    def detect(self, gray_frame):
        faces = self._cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces

    def to_gray_scale(self, frame):
        return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    def draw_retangles(self, bg_frame, faces):
        for (x, y, w, h) in faces:
            cv.rectangle(bg_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return bg_frame