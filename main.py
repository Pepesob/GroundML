from camera import take_picture
from prediction import predict_soil, predictions_with_labels
import time


for i in range(10):
    take_picture()
    print(predictions_with_labels(predict_soil()))
    time.sleep(5)


