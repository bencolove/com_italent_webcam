from io import BytesIO

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
        self.master.geometry(size)

        self.webcam = Webcam()

        # face detector
        self.classifier = FaceClassifier()

        self.initialize_gui()

    def initialize_gui(self):
        # title
        self.master.title("Webcam")

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # # creating a button instance
        # quitButton = tk.Button(self, text="Quit", command=self.client_exit)

        # # placing the button on my window
        # quitButton.place(x=0, y=0)

        # load = tk.Image.open(r'C:\Users\USER\OneDrive\scrambles\draco_momoco_1920_1080.png')
        # render = 

        # use label to display image
        # load = tk.PhotoImage(file=r'C:\Users\USER\OneDrive\scrambles\draco_momoco_1920_1080.png')
        self.image_container = tk.Label()
        self.image_container.place(x=0, y=0)
        self.image_container.pack()

        pool_scheduler = ThreadPoolScheduler(2)
        
        self.subscription = self.webcam.as_observable() \
            .observe_on(pool_scheduler) \
            .map(lambda frame: self._detect_and_draw(frame)) \
            .subscribe(on_next = lambda pil: self.master.after(0, lambda: self.update_image(pil)),
                on_error=lambda err: print(err))

    def _detect_and_draw(self, frame):
        gray = self.classifier.to_gray_scale(frame)
        faces = self.classifier.detect(gray)
        modified_frame = self.classifier.draw_retangles(frame, faces)
        return self._convert_frame_to_pil_image(modified_frame)

    def _convert_frame_to_pil_image(self, frame):
        cv_img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return Image.fromarray(cv_img)
        
    def update_image(self, pil_image):
        new_img = ImageTk.PhotoImage(pil_image)
        self.image_container.image = new_img
        self.image_container.configure(image = new_img)

    def start(self):
        self.mainloop()

    def on_closing(self):
        print('closing down ...')
        self.subscription.dispose()
        self.webcam.release()
        self.master.destroy()
        cv.destroyAllWindows()
        print('quit')
        exit()

if __name__ == '__main__':
    app = APP()
    app.start()