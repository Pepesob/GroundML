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
    return predictions_with_labels(predict_soil())


if __name__ == '__main__':
    uvicorn.run(app, port=config["port"], host=config["ip_addr"])