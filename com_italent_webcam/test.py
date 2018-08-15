import cv2 as cv
import json
import threading
import time
from rx import Observable
from rx.concurrency import ThreadPoolScheduler
from rx.testing import marbles
import tkinter as tk
from datetime import datetime

def test_camera():
    camera = cv.VideoCapture(0)

    ret, frame = camera.read()

    print(f'ret={ret}')

    camera.release()

    cv.imshow('captured', frame)

    cv.waitKey(0)
    cv.destroyAllWindows()

    return frame

def test_classifier(frame):
    from face_classifier import FaceClassifier
    classifier = FaceClassifier()
    gray = classifier.to_gray_scale(frame)
    cv.imshow('gray', gray)
    faces = classifier.detect(gray)
    classifier.draw_retangles(frame, faces)
    cv.imshow('faces', frame)
    cv.waitKey(0)
    cv.destroyAllWindows()

def test_error():
    def verbose_error_handler(status, func_name, err_msg, file_name, line, userdata=''):
        print ("Status = %d" % status)
        print ("Function = %s" % func_name)
        print ("Message = %s" % err_msg)
        print ("Location = %s(%d)" % (file_name, line))
        print ("User data = %r" % userdata)
    cv.redirectError(verbose_error_handler)

    cv.imshow('', None)

def test_multicast():
    print('begin')
    source = Observable.interval(50).take(20) \
        .map(lambda name: f'{name}_modified') \
        .publish() \
        .auto_connect()

    source.subscribe(
            on_next = lambda s: print("Subscriber 1: {0}".format(s)),
            on_error = print)
    source.sample(1000).subscribe(
        on_next = lambda s: print("Subscriber 2: {0} @{1}".format(s, datetime.now())),
        on_error = print)
    print('done')
    input('press any key to quit')

def test_merge():
    print('begin')
    source = Observable.interval(50).take(50) \
        .do_action(lambda i: print(f'{i} @ {datetime.now()}')) \
        .publish() \
        .auto_connect()

    consective = source.map(lambda i: f'consective {i}')

    sample = source.sample(1000).map(lambda i: i + 1000)

    Observable.merge(consective, sample) \
        .subscribe(
            on_next = print,
            on_error = print)
    
    print('done')
    input('press any key to quit')

def test_gui():
    class GUI(tk.Frame):
        def __init__(self, master=tk.Tk(), size="400x300"):
            super().__init__(master)
            self.master = master
            # window close hook
            master.protocol("WM_DELETE_WINDOW", self.on_closing)
            # size of the root window
            self.master.geometry(size)
            label = tk.Label(self.master, text="blar blar blar")
            label.pack()
        
        def on_closing(self):
            self.master.destroy()
    
    gui = GUI()
    gui.mainloop()

def test_marbles():
    s1 = Observable.from_marbles('1---2-3|')
    # s2 = Observable.from_marbles('-a-b-c-|')
    # print(s1.merge(s2).to_blocking().to_marbles())
    print(s1.to_blocking().to_marbles())
    input('press a key')

if __name__ == '__main__':
    # frame = test_camera()
    # test_classifier(frame)
    # test_gui()
    # test_multicast()
    # test_merge()
    # test_marbles()
    print(f'main_thread:={threading.current_thread().name}')
    stop = False
    def subscribe(observer):
        cnt = 0
        while not stop and cnt < 10000:
            observer.on_next(cnt)
            cnt += 1
        def stop_fn():
            print('being disposed')
            stop = True
        return stop_fn
    

    sub = Observable.create(subscribe) \
        .subscribe_on(ThreadPoolScheduler(2)) \
        .buffer_with_count(10) \
        .map(lambda l:l[-1]) \
        .subscribe(on_next=print, on_error=print)

    print('...zzzZZZZ')
    time.sleep(0.5)
    sub.dispose()
    print('disposed()')
    time.sleep(2)
    print('done')


    

    