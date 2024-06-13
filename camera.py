from picamera2 import Picamera2
import shutil
import random
from configuration import Configuration


config = Configuration()

def copy_image():
    try:
        n = random.randint(1,100000000)
        shutil.copy2(config["img_path"], f'{config["img_folder"]}/image_{n}.jpg')
    finally:
        pass



def take_picture():
    picam = Picamera2()
    picam_config = picam.create_preview_configuration(main={"size": (config["img_width_taken"], config["img_height_taken"])})
    picam.configure(picam_config)
    picam.set_controls({"AfMode": 0, "LensPosition": 10})
    picam.start()
    picam.capture_file(config["img_path"])
    copy_image()
    picam.close()


if __name__ == "__main__":
    take_picture()
