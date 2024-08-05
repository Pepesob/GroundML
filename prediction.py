import tensorflow as tf
import tensorflow.lite as tflite
from PIL import Image
import numpy as np
from configuration import Configuration


config = Configuration()
interpreter = tflite.Interpreter(model_path=config["model_path"])


def predictions_with_labels(predictions):
    return {label: float(pred) for label, pred in zip(config["labels"], predictions)}


def get_image_array(path):
    image = Image.open(path).resize((config["img_width"], config["img_height"]))
    return np.array(image, dtype=np.float32)


def predict_soil(img_path):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.allocate_tensors()

    camera_image = get_image_array(img_path)

    interpreter.set_tensor(input_details[0]['index'], [camera_image])

    interpreter.invoke()

    predictions = interpreter.get_tensor(output_details[0]["index"])

    return predictions_with_labels(tf.nn.softmax(predictions[0]))


if __name__ == "__main__":
    print(predict_soil(config["test_img_path"]))
