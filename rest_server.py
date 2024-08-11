import PIL
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import camera
from configuration import Configuration
from prediction import predict_soil
import socket
import time
import asyncio
import threading
import struct


config = Configuration()


def udp_listen():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    receive_address = (("", config["listen_port"]))

    server_socket.bind(receive_address)

    group = socket.inet_aton(config["multicast_listen_addr"])
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("Running udp listener on:", receive_address)

    while True:
        _, addr = server_socket.recvfrom(1024)
        print("Got request from:", addr)

        message = "Broadcast message"
        server_socket.sendto(message.encode("utf-8"), addr)
        print(f"Sending message to: {addr}")
        time.sleep(1)


loop = asyncio.get_event_loop()


app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello World"}


@app.get("/predictions")
async def get_predictions():
    try:
        camera.take_picture()
    except IndexError:
        raise HTTPException(status_code=503, detail="Error with RaspberryPi camera, probably detached camera")
    except ModuleNotFoundError:
        raise HTTPException(status_code=503, detail="Image taking is not supported on this machine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    image = PIL.Image(config["img_path"])
    return predict_soil(image)


@app.get("/image")
async def get_image():
    return FileResponse(config["img_path"])


@app.get("/predictions/path")
async def local_image_prediction(path: str):
    try:
        return predict_soil(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")



if __name__ == '__main__':
    thread = threading.Thread(target=udp_listen)
    thread.daemon = True
    thread.start()
    
    uvicorn.run(app, port=config["port"], host=config["ip_addr"])
    
