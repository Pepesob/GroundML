from fastapi import FastAPI, HTTPException
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

@app.get("/predictions/path")
async def local_image_prediction(path: str):
    try:
        return predict_soil(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Nie znaleziono pliku")

# @app.post("/predictions/image")
# async def local_image_prediction(path: str):
#     print(path)
#     return predict_soil(path)

if __name__ == '__main__':
    uvicorn.run(app, port=config["port"], host=config["ip_addr"])