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

if __name__ == '__main__':
    frame = test_camera()
    test_classifier(frame)