from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import camera
from configuration import Configuration
from prediction import predict_soil
import socket
import time
import threading
import struct


config = Configuration()

"""
This function enables finding ip of the server in the network that this server is connected to
It is done by listening on multicast address specified in `config.json` file in field `multicast_listen_addr`
Multicast packet is send only in the network it was send (the border is router) and interested devices may listen for those packets
"""
def udp_listen():
    # creating socket, an interface to receive data from network
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # setting socket options, this enables to receive multicast packets
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # binding socket to the ip adress and port number, empty string in first item in tuple means binding to default ip, 
    # second items specifies port number
    receive_address = (("", config["listen_port"]))
    server_socket.bind(receive_address)

    # This section actually makes socket listen for multicast packets
    group = socket.inet_aton(config["multicast_listen_addr"])
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("Running udp listener on:", receive_address)

    # The infinite loop that listens for packets
    while True:
        # listening for packet, 1024 is maximum number of bytes that can be received
        # return value is a list of bytes (which we are not interested) and ip adress of the sender
        _, addr = server_socket.recvfrom(1024)
        print("Got request from:", addr)

        # sending a message to ip adress that send previous packet
        message = "Broadcast message"
        server_socket.sendto(message.encode("utf-8"), addr)
        print(f"Sending message to: {addr}")
        time.sleep(1)

"""
Here is section where REST API server is build.

Every function anotaded with @app.<method>(<endpoint>) will create endpoint, process and send data as defined in the function
<method> - one of this: get, put, post, delete
They differ only by convention. There are no strict rules for this.
"""

# Initializing server using FastAPI
app = FastAPI()

# Test endpoint, should always work
@app.get("/")
async def hello():
    return {"message": "Hello World"}

# Endpoint that makes photo with camera, makes a prediction about soil and returns resutls
@app.get("/predictions")
async def get_predictions():
    # Try blok "tries" to execute code, if an exception was raised while executing, catches this exception and decides what to do based
    # on raised exception
    try:
        # Takes the picture from camera and saves the result to file
        camera.take_picture()
    except IndexError: # This error is usually thrown when RaspberryPi Camera is not connected
        raise HTTPException(status_code=503, detail="Error with RaspberryPi camera, probably detached camera")
    except ModuleNotFoundError: # This error means that this server is not suposed to make predictions based on live photo taken
        raise HTTPException(status_code=503, detail="Image taking is not supported on this machine")
    except Exception as e: # General exception, this block executes if diffrent excpetion was raised than above ones
        raise HTTPException(status_code=500, detail=str(e))

    # This loads the image from the file
    image = Image.open(config["img_path"])

    # this predicts what soil is shown on image and returns json with probability of which soil the photo is
    return predict_soil(image)


# Function to retreive previously taken and predicted photo
@app.get("/image")
async def get_image():
    return FileResponse(config["img_path"])

@app.get("/drl")
async def get_image():
    return FileResponse("test.drl")

# Debug function, relict of the past
@app.get("/predictions/path")
async def local_image_prediction(path: str):
    try:
        image = Image.open(path)
        return predict_soil(image)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")



if __name__ == '__main__':
    # Running the discovery feature in the background
    thread = threading.Thread(target=udp_listen)
    thread.daemon = True
    thread.start()
    
    # Starting REST API server
    uvicorn.run(app, port=config["port"], host=config["ip_addr"])
    
