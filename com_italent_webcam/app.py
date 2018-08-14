from io import BytesIO
import time
import json
import threading
import sys

import tkinter as tk
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk

from rx import Observable, Observer 
from rx.concurrency import ThreadPoolScheduler

from webcam import Webcam
from face_classifier import FaceClassifier

class APP(tk.Frame):
    def __init__(self, master=tk.Tk(), size="400x300"):
        super().__init__(master)
        self.master = master
        # window close hook
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        # size of the root window
        self.master.geometry(size)
        # webcam instance
        self.webcam = Webcam()

        # face detector
        self.classifier = FaceClassifier()
        # initialize visual components on the window
        self.initialize_gui()
        # handler to stop streams
        self.webcam_subscription = None
        self.api_subscription = None
        # temporarily useage
        self._timer = 1 

    def initialize_gui(self):
        """ draw visual items on the window
        """
        # title
        self.master.title("Webcam")

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # label as container to display video
        self.image_container = tk.Label(self)
        # self.image_container.place(x=0, y=0)
        self.image_container.pack()

        # label as container to display text
        self.text_container = tk.Label(self, 
            text='age:18 \n gender:Male', 
            justify=tk.CENTER)
        self.text_container.pack(side='bottom')

    def _detect_and_draw(self, frame):
        """ 
        step 1. convert cv_frame to gray scale
        step 2. detect faces in the gray frame
        step 3. draw rectangles over the face locations 
        """
        gray = self.classifier.to_gray_scale(frame)
        faces = self.classifier.detect(gray)
        modified_frame = self.classifier.draw_retangles(frame, faces)
        return self._convert_frame_to_pil_image(modified_frame)

    def _convert_frame_to_pil_image(self, frame):
        """ convert a cv_frame to PIL image """
        cv_img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return Image.fromarray(cv_img)
        
    def update_image(self, pil_image):
        """ update UI with PIL image """
        new_img = ImageTk.PhotoImage(pil_image)
        self.image_container.image = new_img
        self.image_container.configure(image = new_img)

    def analyze_face(self, face):
        """
        call remote API service for an analyzed face
        """
        # minics remote API service
        time.sleep(0.2)
        self._timer += 1
        data = {
            'age': self._timer,
            'gender': 'F'
        }
        return Observable.just(json.dumps(data)) 

    def update_text(self, json_text):
        """ update UI with json_text """
        self.text_container.config(text=json_text)

    def start(self):
        """ call it to let the GUI run """
        self._start_stream()
        self.mainloop()
        print('outa mainloop')
        
    def _start_stream(self):
        # setup source
        pool_scheduler = ThreadPoolScheduler(2)
        
        source = self.webcam.as_observable() \
            .observe_on(pool_scheduler) \
            .tap(lambda frame: print(f'thread name = {threading.current_thread().name}'))

        # setup webcam stream
        self.webcam_subscription = source \
            .map(lambda frame: self._detect_and_draw(frame)) \
            .subscribe(
                on_next = lambda pil: self.master.after(0, lambda: self.update_image(pil)),
                on_error=print)
        # setup api stream
        self.api_subscription = source \
            .flat_map(lambda frame: self.analyze_face(frame)) \
            .do_action(print) \
            .subscribe(
                on_next = lambda json_resp: self.master.after(0, lambda: self.update_text(json_resp)),
                on_error=print)

    def on_closing(self):
        print('closing down ...')
        print('stop streams')
        self.webcam_subscription and self.webcam_subscription.dispose()
        self.api_subscription and self.api_subscription.dispose()
        print('release camera')
        self.webcam.release()
        print('destroy windows')
        self.master.destroy()
        cv.destroyAllWindows()
        print('system exit')
        sys.exit()

if __name__ == '__main__':
    app = APP()
    app.start()