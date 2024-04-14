from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
import json
import asyncio
import requests
from aiortc.contrib.signaling import BYE, TcpSocketSignaling
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.mediastreams import VideoStreamTrack
from multiprocessing import Process, RawArray, Lock
from ctypes import c_uint8
import asyncio
from aiortc.mediastreams import MediaStreamError
import numpy as np

import cv2


######################################################################
#                       CV2 Window
######################################################################
def window(cbuf):
    run = True
    while run:
        color = np.frombuffer(cbuf, np.uint8, shape[0] * shape[1] * shape[2])
        color = color.reshape(shape)
        cv2.imshow("Display", color)
        cv2.waitKey(1)


######################################################################
#                       Video Capture Track
######################################################################

shape = (480, 640, 3)
cbuf = RawArray(c_uint8, shape[0] * shape[1] * shape[2])
# color = np.frombuffer(cbuf, np.uint8, shape[0] * shape[1] * shape[2])
# color = color.reshape(shape)
# color[:, :] = (255, 0, 0)
clock = Lock()


async def consume_track(track):
    global cbuf, clock
    color = np.frombuffer(cbuf, np.uint8, shape[0] * shape[1] * shape[2])
    while True:
        try:
            frame = await track.recv()
            np.copyto(color, frame.to_ndarray(format="bgr24").flatten())
        except MediaStreamError:
            return


class VideoMediaStream:
    def __init__(self):
        self.__tracks = {}

    def addTrack(self, track):
        if track not in self.__tracks:
            self.__tracks[track] = None

    async def start(self):
        for track, task in self.__tracks.items():
            if task is None:
                self.__tracks[track] = asyncio.ensure_future(consume_track(track))

    async def stop(self):
        for task in self.__tracks.values():
            if task is not None:
                task.cancel()
        self.__tracks = {}


# Signaling Server - Flask Server
SIGNALING_SERVER = "127.0.0.1"
PORT = 8080
# SIGNALING_SERVER = "https://hello.autoscale.ca/"
# PORT = 443


async def streamer(
    peer_connection: RTCPeerConnection,
    recorder: VideoMediaStream,
    Ttcp_socket_signalling: TcpSocketSignaling,
):
    def add_tracks():
        peer_connection.addTrack(VideoStreamTrack())  #
        print("Added Video Track")

    @peer_connection.on("track")
    async def on_track(track):
        print("Receiving %s" % track.kind)
        if track.kind == "video":
            recorder.addTrack(track)
            print("Added Video")
            await recorder.start()
            print("Recorder Started")

    await Ttcp_socket_signalling.connect()
    print("Signalling Connect")

    # Waiting for Signal Answer
    while True:
        responseObject = await Ttcp_socket_signalling.receive()

        if isinstance(responseObject, RTCSessionDescription):
            # Set Remte SDP into Remote Description
            await peer_connection.setRemoteDescription(responseObject)
            # Create Answer from Remote SDP
            await peer_connection.setLocalDescription(
                await peer_connection.createAnswer()
            )

            print("Adding Video Track")
            add_tracks()

            # Respond to Server with Answer
            await Ttcp_socket_signalling.send(peer_connection.localDescription)
            print("Answer sent to Server")
        elif isinstance(responseObject, RTCIceCandidate):
            print("adding ice candidate")
            await peer_connection.addIceCandidate(responseObject)
            print("added ice candidate")
        elif responseObject is BYE:
            print("Exiting...")
            break

    print("Connection Established - Client")


def receiveStream(buf):
    global cbuf
    cbuf = buf

    tcp_socket_signalling = TcpSocketSignaling(SIGNALING_SERVER, port=PORT)
    # Create Peer Connection
    peer_connection = RTCPeerConnection()
    print("Peer Connection")

    # Media Reader
    recorder = VideoMediaStream()

    # Create the Session Description Protocol
    asyncio.run(streamer(peer_connection, recorder, tcp_socket_signalling))


if __name__ == "__main__":
    # print("Main")
    displayer = Process(target=window, args=[cbuf])
    displayer.start()
    receiveStream(cbuf)
