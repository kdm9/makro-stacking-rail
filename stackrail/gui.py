import sys
from time import time, sleep
from .camera import CameraInterface
from .serialctrl import SerialController 

from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QFileDialog,
)
from PyQt6.QtGui import (
        QImage,
        QPixmap,
)
from PyQt6.QtCore import (
        pyqtSlot as Slot,
        pyqtSignal as Signal,
        QRunnable,
        QThreadPool,
)
from PyQt6 import uic

class LiveViewThread(QRunnable):
    def __init__(self, label):
        super().__init__()
        self.cam = CameraInterface()
        self.label = label
        self.show = True
        self.kill = False

    
    def run(self):
        while not self.kill:
            sleep(1/15)
            if self.show:
                img = self.cam.preview_one()
                imgQT = QImage()
                imgQT.loadFromData(img)
                pixMap = QPixmap.fromImage(imgQT)
                self.label.setPixmap(pixMap)


class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("stackrail/main.ui", self)
        self.threadpool = QThreadPool()

        self.camthr = LiveViewThread(self.img_main)
        self.camthr.show = False
        self.threadpool.start(self.camthr)
        self.sr = SerialController()

        self.s_update_settings()
        self.outdir = "."

    @Slot(bool)
    def s_toggle_liveview(self, val):
        self.camthr.show = val
        if not val:
            self.img_main.clear()

    @Slot()
    def s_set_speed(self):
        speed_setting = self.box_speed.value()
        print("SET SPEED", speed_setting)
        print(self.sr.speed(speed_setting))

    @Slot()
    def s_btn_move(self):
        self.move(float(self.box_move.value()))

    @Slot()
    def s_btn_stack(self):
        nsteps = int(self.box_stack_nsteps.value())
        for i in range(nsteps):
            self.move(float(self.box_stack_stepsize.value()))
            with open(f"{self.outdir}/{i}.CR3", "wb") as fh:
                fh.write(self.camthr.cam.take_photo())

    @Slot()
    def s_choose_outdir(self):
        self.outdir = QFileDialog.getExistingDirectory(self,
                caption="Choose stacking output dir")
        self.lbl_outdir.setText(self.outdir)


    @Slot()
    def s_update_settings(self):
        steps_per_rev = int(self.box_steps.value())
        pitch = float(self.box_pitch.value())
        usteps = int(self.box_microstep.currentText())
        self.movements_per_mm = (steps_per_rev * usteps) / pitch
        print("MMM", self.movements_per_mm)
        print(self.sr.usteps(usteps))
        self.lab_stepsize.setText(f"{1000*1/self.movements_per_mm:0.2f}μm")

    def move(self, move_mm):
        total_move = int(self.movements_per_mm * move_mm)
        print("MSTP", total_move)
        while total_move > 2**15-1 or total_move < -2**15-1:
            if total_move > 0:
                print(self.sr.move(2**15-1))
                total_move -= 2**15-1
            else:
                print(self.sr.move(-2**15-1))
                total_move += 2**15-1
        print(self.sr.move(total_move))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Main()
    form.show()
    retval = app.exec()
    form.camthr.kill = True
    sys.exit(retval)
