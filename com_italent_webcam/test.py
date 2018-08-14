import cv2 as cv

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

if __name__ == '__main__':
    frame = test_camera()
    test_classifier(frame)

    