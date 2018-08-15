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
from rx.concurrency import TkinterScheduler,ThreadPoolScheduler

from webcam import Webcam
from face_classifier import FaceClassifier
from service import FaceService

class APP(tk.Frame):
    def __init__(self, master=tk.Tk(), size="400x300"):
        super().__init__(master)
        self.master = master
        # window close hook
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        # size of the root window
        self.master.geometry(size)
        # webcam instance
        # self.webcam = Webcam()

        # face detector
        self.classifier = FaceClassifier()

        self.service = FaceService()

        # initialize visual components on the window
        self.initialize_gui()
        # handler to stop streams
        self.webcam_subscription = None
        self.api_subscription = None
        self.service_subscription = None
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
        # self._stream()
        self.mainloop()
        print('outa mainloop')

    def _stream(self):
        # pool_scheduler = ThreadPoolScheduler(2)
        scheduler = TkinterScheduler(self.master)
        self.service_subscription = self.service.as_observable() \
            .map(lambda frame: self._convert_frame_to_pil_image(frame)) \
            .observe_on(scheduler) \
            .subscribe(
                on_next = lambda pil_image: self.master.after(0, lambda: self.update_image(pil_image)),
                on_error=print)
        
    def _start_stream(self):
        # setup source
        # pool_scheduler = ThreadPoolScheduler(2)
        ui_scheduler = TkinterScheduler(self.master)
        # self.service_subscription = self.service.as_observable()

        self.service_subscription = self.service.as_observable() \
            .map(self._convert_frame_to_pil_image) \
            .observe_on(ui_scheduler) \
            .subscribe(
                on_next = lambda pil: self.master.after(0, lambda: self.update_image(pil)),
                on_error=print)

        self.api_subscription = self.service.api_stream() \
            .subscribe(
                on_next = lambda rst: self.master.after(0, lambda: self.update_text(json.dumps(rst))),
                on_error=print
            )
       
    def on_closing(self):
        prefix = 'app.on_closing'
        print('{} - stop streams'.format(prefix))
        if self.api_subscription:
            print('{} - stop aip stream'.format(prefix))
            self.api_subscription.dispose()
        if self.service_subscription:
            print('{} - stop webcam stream'.format(prefix))
            self.service_subscription.dispose()
      
        print('{} - destroy windows'.format(prefix))
        self.master.destroy()
        cv.destroyAllWindows()
        print('{} - system exit'.format(prefix))
        time.sleep(5)
        sys.exit()

if __name__ == '__main__':
    app = APP()
    app.start()