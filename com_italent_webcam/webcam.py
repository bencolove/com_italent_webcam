import cv2 as cv
from rx import Observable, Observer
from rx.subjects import Subject 
from rx.concurrency import NewThreadScheduler, \
    ThreadPoolScheduler, \
    TkinterScheduler

class Webcam:
    def __init__(self):
        self._cap = cv.VideoCapture(0)
        self._stop_webcam = False
        # set up observable using multithreading
        producer_thread = ThreadPoolScheduler(1)

        self.observable = Observable.create(self._observer_fn) \
            .subscribe_on(producer_thread) \
            .publish() \
            .auto_connect()

        # self._source = Observable.interval(1) \
        #     .take(1000) \
        #     .subscribe_on(NewThreadScheduler()) \
        #     .do_action(print) \
        #     .map(lambda i: self._cap.read()[1]) \
        #     .publish() \
        #     .auto_connect()

    def as_observable(self):
        # wrap it into Observable
        return self.observable

    def _observer_fn(self, observer):
        while True and not self._stop_webcam:
            ok, frame = self._cap.read()
            if ok:
                observer.on_next(frame)
            else:
                observer.on_error('Cannot read camera device')
                self.release()
                break

        return self.release

    def release(self):
        print('webcam.release')
        self._stop_webcam = True
        self._cap.release()