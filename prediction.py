try:
    import tflite_runtime.interpreter as tflite
except ModuleNotFoundError:
    import tensorflow.lite as tflite

import PIL
import numpy as np
from configuration import Configuration


config = Configuration()
interpreter = tflite.Interpreter(model_path=config["model_path"])


def predictions_with_labels(predictions):
    return {label: float(pred) for label, pred in zip(config["labels"], predictions)}


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def predict_soil(soil_image: PIL.Image):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.allocate_tensors()

    image_array = np.array(soil_image.resize((config["img_width"], config["img_height"])), dtype=np.float32)

    interpreter.set_tensor(input_details[0]['index'], [image_array])

    interpreter.invoke()

    predictions = interpreter.get_tensor(output_details[0]["index"])

    return predictions_with_labels(softmax(predictions[0]))


if __name__ == "__main__":
    print(predict_soil(config["test_img_path"]))
