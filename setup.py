from setuptools import setup
import io


def load_dependencies():
    filename = 'requirements.txt'
    encoding = 'utf-8'
    buf = []
    with io.open(filename, encoding=encoding) as f:
        return [line.strip() for line in f.readlines()]


setup(name='com.italent.webcam', \
    vserion='0.0.1', \
    description='Webcam test', \
    url='', \
    author='Roger Huang', \
    author_email='', \
    license='MIT', \
    install_require=load_dependencies(), \
    packages=['com_italent_webcam'], \
    zip_safe=False)

