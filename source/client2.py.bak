import pygame

import asyncio
from aiortc import (
  RTCPeerConnection,
  RTCSessionDescription,
  RTCIceCandidate,
)
from aiortc.mediastreams import MediaStreamError, VideoStreamTrack
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.contrib.signaling import TcpSocketSignaling, BYE

from multiprocessing import Process, RawArray, Lock
from ctypes import c_uint8
import numpy as np

shape = (480, 640, 3)
cbuf = RawArray(c_uint8, shape[0] * shape[1] * shape[2])

async def consume_track(track):
  global cbuf
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

pc = None
remoteStream = None
signaling = None

def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )

async def run():
  global pc

  @pc.on("track")
  async def on_track(track):
    if track.kind == "video":
      remoteStream.addTrack(track)
      await remoteStream.start()

  await signaling.connect()

  while True:
    obj = await signaling.receive()
    if isinstance(obj, RTCSessionDescription):
      await pc.setRemoteDescription(obj)
      pc.addTrack(VideoStreamTrack())
      await pc.setLocalDescription(await pc.createAnswer())
      await signaling.send(pc.localDescription)

    elif isinstance(obj, RTCIceCandidate):
      await pc.addIceCandidate(obj)

    elif obj is BYE:
      print("Exiting")
      return

def stream(buf):
  global remoteStream, signaling, pc, clock, cbuf
  cbuf = buf
  signaling = TcpSocketSignaling("127.0.0.1", 8080)
  pc = RTCPeerConnection()
  remoteStream = VideoMediaStream()
  asyncio.run(run())

if __name__ == "__main__":
  try:
    pygame.init()
    screen = pygame.display.set_mode((shape[1], shape[0]))
    process = Process(target=stream, args=[cbuf])
    process.start()
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
      pybuf = pygame.image.frombuffer(cbuf, (shape[1], shape[0]), "BGR")
      screen.blit(pybuf, (0, 0))
      pygame.display.flip()
  except KeyboardInterrupt:
    pass
  finally:
    process.terminate()
