import tflite_runtime.interpreter as tflite
from PIL import Image
import numpy as np

image_width = 180
image_height = 180

image_path = "./test_soil_black.jpg"
model_path = "./soil_recognition_lite"

interpreter = tflite.Interpreter(model_path=model_path)

def get_image_array(path):
    image = Image.open(path).resize((image_width, image_height))
    return np.array(image,dtype=np.float32)


def predict_soil():
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.allocate_tensors()

    camera_image = get_image_array(image_path)

    interpreter.set_tensor(input_details[0]['index'], [camera_image])

    interpreter.invoke()

    predictions = interpreter.get_tensor(output_details[0]["index"])

    return predictions[0]


