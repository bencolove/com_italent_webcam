import cv2 as cv

__all__ = ['Tracker']

(major_ver, minor_ver, subminor_ver) = (cv.__version__).split('.')
# Set up tracker.
# Instead of MIL, you can also use
tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
# by default use 'KCF'
tracker_type = tracker_types[2]

class Tracker:
    def __init__(self):
        self._setup_tracker()

    def _setup_tracker(self):
        if int(minor_ver) < 3:
            tracker = cv.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                tracker = cv.TrackerBoosting_create()
            if tracker_type == 'MIL':
                tracker = cv.TrackerMIL_create()
            if tracker_type == 'KCF':
                tracker = cv.TrackerKCF_create()
            if tracker_type == 'TLD':
                tracker = cv.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                tracker = cv.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                tracker = cv.TrackerGOTURN_create()
            if tracker_type == 'MOSSE':
                tracker = cv.TrackerMOSSE_create()
            if tracker_type == "CSRT":
                tracker = cv.TrackerCSRT_create()
        self._tracker = tracker
        self._tracker_type = tracker_type
    
    @property
    def tracker_type(self):
        return self._tracker_type

    def set_bounding(self, frame, box):
        # Initialize tracker with first frame and bounding box
        ok = self._tracker.init(frame, tuple(box))
        return ok
    
    def update_frame(self, frame):
        # Update tracker
        ok, box = self._tracker.update(frame)
        return (ok, box) 