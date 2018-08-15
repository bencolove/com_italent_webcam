import cv2 as cv
import json
import random
from datetime import datetime

import requests

from rx import Observable
from rx.subjects import Subject

from config import config as conf
from webcam import Webcam
from tracker import Tracker
from face_classifier import FaceClassifier

class FaceService:
    def __init__(self):
        self._debug = conf['debug'] or False
        self._cv_debug = conf['cv_debug'] or False
        self.webcam = Webcam()
        self.tracker = Tracker()
        self.detector = FaceClassifier()
        self.last_tick = cv.getTickCount()
        self.got_face = False

        self.sample_stream = self.webcam.as_observable() \
            .sample(1000) \
            .do_action(lambda f: self._debug and print('sampled at {}'.format(datetime.now()))) \
            .map(self.detect) \
            .publish() \
            .auto_connect() 

    def as_observable(self):
        # frame stream
        frame_stream = self.webcam.as_observable()

        # detect stream
        # sample_stream = self.webcam.as_observable() \
        #     .sample(1000) \
        #     .do_action(lambda f: print(f'sampled at {datetime.now()}')) \
        #     .map(self.detect) \
        #     .publish() \
        #     .auto_connect()
            

        detect_stream = self.sample_stream \
            .do_action(self.init_tracker)     

        return frame_stream \
            .combine_latest(detect_stream, self.merge_detect_result)

    def api_stream(self):
        return self.sample_stream \
            .filter(lambda rst: rst['box'] is not None) \
            .map(lambda rst: rst['frame']) \
            .flat_map(FaceApi().get_result_as_observable)     

    # def track_or_detect(self, data):
    #     self._debug and print('merge')
    #     box = None
    #     frame = None
    #     if isinstance(data, dict):
    #         # detect result
    #         box = data['box']
    #         frame = data['frame']
    #         self._debug and print('detect result {}'.format(box))
    #         if box:
    #             self.tracker.set_bounding(frame, box)
    #         else:
    #             return frame
    #     else:
    #         self._debug and print('frame')
    #         # frame
    #         frame = data

    #     if self.got_face:
    #         ok, box_now = self.tracker.update_frame(frame)
    #         self._debug and print('update box={}'.format(box_now))
    #         if ok: 
    #             box = [int(x) for x in box_now]
    #         else:
    #             return frame
        
    #         # update box
    #         self._debug and print('before draw box={}'.format(box))
    #         frame_now = self.detector.draw_retangles(frame, [box])
    #         return frame_now
    #     else:
    #         return frame    

    def detect(self, frame):
        self._debug and print('try to detect')
        gray = self.detector.to_gray_scale(frame)
        boxes = self.detector.detect(gray)
        result = {
                'box': None,
                'frame': frame
            }
        if len(boxes) == 0:
            self._debug and print('detect failed at {}'.format(datetime.now()))
            self.got_face = False
        else:
            # detect succeeded
            # merge into tracker
            result['box'] = [x for x in boxes[0]]
            self.got_face = True
            self._debug and print("face detected at {}".format(result['box']))
        return result

    def init_tracker(self, data):
        self._debug and print('init_tracker')
        if data['box']:
            box = data['box']
            frame = data['frame']
            self._debug and print('  tracker.init box={}'.format(box))
            self.tracker = Tracker()
            self.tracker.set_bounding(frame, box)

    def merge_detect_result(self, frame, result):
        if result['box']:
            # detectd a face, update frame
            ok, box = self.tracker.update_frame(frame)
            if ok:
                box = [int(x) for x in box]
                # self._debug and print('update box={}'.format(box))
                frame_now = self.detector.draw_retangles(frame, [box])
                # Display tracker type on frame
                cv.putText(frame, 
                    self.tracker.tracker_type + " Tracker", (100,20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
                return frame_now
            else:
                return frame
        else:
            return frame

    # def _track_or_detect(self, frame):
    #     tick = cv.getTickCount()
    #     ticked = tick - self.last_tick
    #     self.last_tick = tick
    #     print(f'got_face={self.got_face} ticked={ticked}')

    #     if not self.got_face or ticked // 1000000 > 0:
    #         # time to detect again
    #         gray = self.detector.to_gray_scale(frame)
    #         boxes = self.detector.detect(gray)
    #         if len(boxes) == 0:
    #             self.got_face = False
    #             return frame
    #         else:
    #             self.got_face = True
    #             box = tuple(boxes[0])
    #             self.tracker.set_bounding(frame, box)
    #             ok, box_now = self.tracker.update_frame(frame)
    #             # draw box
    #             box_now = [int(x) for x in box_now]
    #             frame_now = self.detector.draw_retangles(frame, [box_now])
    #             return frame_now
    #     elif self.got_face:
    #         # update face box
    #         print('update bounding')
    #         ok, box_now = self.tracker.update_frame(frame)
    #         # draw box
    #         box_now = [int(x) for x in box_now]
    #         frame_now = self.detector.draw_retangles(frame, [box_now])
    #         return frame_now
    #     else:
    #         # no face got
    #         return frame


class FaceApi:
    def __init__(self):
        self._debug = conf['debug']
        self.url = conf['face_api_url']

    def get_result_as_observable(self, frame):
        return Observable.create(self._observer_fn)

    def _observer_fn(self, observer):
        self._debug and print('--> FaceApi @{}'.format(datetime.now()))
        r = requests.get(self.url)
        if r.status_code == 200:
            result = self._gen_random_text(r.text)
            self._debug and print('{} <-- FaceApi'.format(result))
            observer.on_next(result)
            # observer.on_complete()
        else:
            self._debug and print('error [code={} body={}] <-- FaceApi'.format(r.status_code, r.text))
            observer.on_error(r)

    def _gen_random_text(self, text):
        rand_list = json.loads(text)
        index = random.randint(0, len(rand_list)-1)
        content = rand_list[index]

        result = {
            'age': int(content) % 100,
            'gender': 'F' if int(content) % 2 == 0 else 'M' 
        }
        return result
