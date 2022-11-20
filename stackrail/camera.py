import locale
from pathlib import Path

import gphoto2 as gp

class CameraInterface(object):
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera))

    def take_photo(self):
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        camera_file = self.camera.file_get(file_path.folder, file_path.name,
                                      gp.GP_FILE_TYPE_NORMAL)
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        return bytes(memoryview(file_data))

    def preview_one(self):
        camera_file = gp.check_result(gp.gp_camera_capture_preview(self.camera))
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        return bytes(memoryview(file_data))

    def __del__(self):
        if self.camera is not None:
            gp.check_result(gp.gp_camera_exit(self.camera))

if __name__ == "__main__":
    cam = CameraInterface()
    cam.take_photo(".")
