from .camera import CameraInterface
from .serialctrl import SerialController 
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from time import sleep

class LiveViewThread(QRunnable):
    def __init__(self, label):
        super().__init__(self)
        self.cam = CameraInterface()
        self.label = label
        self.keep_going = True
    
    @Slot()
    def run(self):
        while self.keep_going:
            sleep(1/15)
            img = self.cam.preview_one()
            imgQT = QImage()
            imgQT.loadFromData(img)
            pixMap = QPixmap.fromImage(imgQT)
            self.label.setPixmap(pixMap)




def demo():
    sr = SerialController()
    print(sr.speed(200))
    app = QApplication( sys.argv )
    threadpool = QThreadPool()
    label = QLabel()
    label.resize(600,400)
    label.show()
    camthr = LiveViewThread(label)
    threadpool.start(camthr)
    print(sr.usteps(4))
    print(sr.move(200*4*10))
    print(sr.move(-200*4*10))
    app.exec_()
    camthr.keep_going = False

if __name__ == "__main__":
    demo()
