from flask import Flask, render_template, request, Response
import json
import uuid

app = Flask(__name__)

data = {
    "request_id": "234252342adsfasdf",
    "id": "SampleOffer",
    "type": "offer",
    "sdp": "test",
}


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/status")
def status():
    return Response('{"status": "ok"}', status=200, mimetype="application/json")


# 1. Client #1 - Create an Session Description Protocol (SDP) Offer, send to server
@app.route("/offer", methods=["POST"])
def offer():
    request_data = request.get_json()
    # Generate a UUID to store with Post Request
    request_id = uuid.uuid4().hex
    # Check for HTTP request type
    if request_data["type"] == "offer":
        # Store the offer in dictionary with key: `offer`
        # Generate a UUID to store with Post Request
        request_id = uuid.uuid4().hex
        data["offer"] = {
            "request_id": request_id,
            "id": request_data["id"],
            "type": request_data["type"],
            "sdp": request_data["sdp"],
        }
        return Response("OK", status=201)
    else:
        return Response(message="Error: JSON", status=400)


# 2. Client #2 - Requests/Receives an offer, creates an Answer
@app.route("/answer", methods=["POST"])
def answer():
    request_data = request.get_json()
    # Check for HTTP request type
    if request_data["type"] == "answer":
        # Store the offer in dictionary with key: `offer`
        # Generate a UUID to store with Post Request
        request_id = uuid.uuid4().hex
        data["answer"] = {
            "request_id": request_id,
            "id": request_data["id"],
            "type": request_data["type"],
            "sdp": request_data["sdp"],
        }
        return Response(status=201)
    else:
        return Response(status=400)


# 3. Client #2 - Sends Answer back
@app.route("/getOffer", methods=["GET"])
def getOffer():
    if "offer" in data:
        json_object = json.dumps(data["offer"])
        del data["offer"]
        return Response(json_object, status=200, mimetype="application/json")
    else:
        return Response(status=503)


# 4. Client #1 - Receives the Answer
@app.route("/getAnswer", methods=["GET"])
def getAnswer():
    if "answer" in data:
        # Take what is stored in dictionary if exists.
        json_object = json.dumps(data["answer"])
        del data["answer"]
        # Return to client
        return Response(json_object, status=200, mimetype="application/json")
    else:
        return Response(status=503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
