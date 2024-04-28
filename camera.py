from picamera2 import Picamera2
from configuration import Configuration


config = Configuration()


def take_picture():
    picam = Picamera2()
    picam_config = picam.create_preview_configuration(main={"size": (config["img_width"], config["img_height"])})
    picam.configure(picam_config)
    picam.start()
    picam.capture_file(config["img_path"])
    picam.close()


if __name__ == "__main__":
    take_picture()
