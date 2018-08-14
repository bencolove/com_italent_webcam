import cv2 as cv
from rx import Observable, Observer
from rx.subjects import Subject 
from rx.concurrency import ThreadPoolScheduler

class Webcam:
    def __init__(self):
        self._cap = cv.VideoCapture(0)
        # self._subject = Subject()

        self._source = Observable.interval(100) \
            .take(100) \
            .do_action(print) \
            .map(lambda i: self._cap.read()[1]) \
            .publish() \
            .auto_connect()

    def as_observable(self):
        # wrap it into Observable
        return self._source

    def release(self):
        self._cap.release()