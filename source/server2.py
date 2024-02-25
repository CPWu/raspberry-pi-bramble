import asyncio

from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
)
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from aiortc.contrib.media import MediaPlayer

####
from av import VideoFrame
from av.frame import Frame
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    RTCConfiguration,
    RTCIceServer,
    MediaStreamTrack,
)
from aiortc.mediastreams import MediaStreamError, VideoStreamTrack
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from aiortc.contrib.media import MediaPlayer
import fractions
import cv2
import time

FPS = 60
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / FPS
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

from multiprocessing import Process, RawArray, Lock
from ctypes import c_uint8
import numpy as np

shape = (480, 640, 3)
cbuf = RawArray(c_uint8, shape[0] * shape[1] * shape[2])


class VideoCaptureTrack(MediaStreamTrack):
    kind = "video"
    _start: float
    _timestamp: int

    def __init__(self, path="/dev/video0"):
        super().__init__()
        self.camera = cv2.VideoCapture(path)
        _, image = self.camera.read()
        # cv2.imshow("Test Image", image)
        # cv2.waitKey(1)

    async def next_timestamp(self):
        if self.readyState != "live":
            raise MediaStreamError

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE

    async def recv(self) -> Frame:
        frame = None
        _, img = self.camera.read()
        # print(time.time())
        if img is not None:
            img = cv2.resize(img, (640, 480))
            # color = np.frombuffer(cbuf, np.uint8, shape[0] * shape[1] * shape[2])
            # np.copyto(color, img.flatten())
            frame = VideoFrame.from_ndarray(img, format="bgr24")
            pts, time_base = await self.next_timestamp()
            frame.pts = pts
            frame.time_base = time_base
        return frame


######################################################################
#                       WebRTC Streamer
######################################################################

pc = None
media_track = None
signaling = None


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )


async def run():
    await signaling.connect()  # doesnt do anything

    video_sender = pc.addTrack(media_track)
    force_codec(pc, video_sender, "video/H264")
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)

    while True:
        obj = await signaling.receive()
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)

        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)

        elif obj is BYE:
            print("Exiting")
            return


def stream(host="127.0.0.1", port=8080):
    global media_track, signaling, pc
    signaling = TcpSocketSignaling(host, port)
    pc = RTCPeerConnection()
    # media_track = MediaPlayer('/dev/video2', format='v4l2', options={'video_size': '640x480'})
    # options = {"framerate": "30", "video_size": "640x480"}
    # media_track = MediaPlayer("default:none", format="avfoundation", options=options)
    media_track = VideoCaptureTrack(0)
    asyncio.run(run())


if __name__ == "__main__":
    # displayer = Process(target=window, args=[cbuf])
    # displayer.start()
    stream()
