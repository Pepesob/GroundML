from fastapi import FastAPI
import uvicorn
from configuration import Configuration
from prediction import predict_soil, predictions_with_labels

config = Configuration()

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello World"}

@app.get("/predictions")
async def get_predictions():
    return predict_soil(config["test_img_path"])

@app.post("/predictions/path")
async def local_image_prediction(path: str):
    return predict_soil(path)

# @app.post("/predictions/image")
# async def local_image_prediction(path: str):
#     print(path)
#     return predict_soil(path)

if __name__ == '__main__':
    uvicorn.run(app, port=config["port"], host=config["ip_addr"])