from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import json
import asyncio
import requests

# Signaling Server - Flask Server
SIGNALING_SERVER = "http:/localhost:5000"

ID = "Offerer01"

# Stun Server 
stun_server = RTCIceServer(urls=["stun:stun1.1.google.com:19302","stun:stun2.1.google.com:19302"])

async def main():
    # WebRTC is capable of three different types of channels: data, video, audio.
    print("Starting..")
    peer_connection = RTCPeerConnection()
    # Create Data Channel
    channel = peer_connection.createDataChannel('Chat')

    # Function in function
    async def send_pings(channel):
        num = 0
        while True:
            msg = "From offerer: {}".format(num)
            print("Sending via RTC Datachannel: ", msg)
            channel.send(msg)
            num+=1
            await asyncio.sleep(1)

    # Events that may occur in the channel
    @channel.on("open")
    def on_open():
        print("Channel Opened")
        channel.send("Hello from Offerer via data hannel")
        asyncio.ensure_future(send_pings(channel))

    @channel.on("message")
    def on_message(message):
        print("Received via RTC Data Channel", message)

    # Create SDP
    await peer_connection.setLocalDescription(await peer_connection.createOffer)
    # Create Message of JSON Object to pass Offer
    message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
    # Take offer and send to signal server
    req = requests.post(SIGNALING_SERVER + "/offer", data=message)
    print(req.status_code)

    # Polling
    while True:
        resp = requests.get(SIGNALING_SERVER + "/getAnswer")
        if resp.status_code == 503:
            print("Answer is not ready yet, trying again...")
            await asyncio.sleep(1)
        elif resp.status_code == 200:
            data = resp.json()
            if data["type"] == "answer":
                rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await peer_connection.setRemoteDescription(rd)
                print(peer_connection.remoteDescription)
                while True:
                    print("Ready")
                    await asyncio.sleep(1)
            else:
                print("Wrong session description type.")
            break
        print(resp.status_code)
        
    # Start main function asynchronously
    asyncio.run(main())