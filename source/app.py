from flask import Flask, render_template, request, Response
import json

app = Flask(__name__)

data = {}

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/status")
def status():
    return Response('{"status": "ok"}', status = 200, mimetype="application/json")

# 1. Client #1 - Create an Session Description Protocol (SDP) Offer, send to server
@app.route("/offer", methods = ["POST"])
def offer():
    # Check for HTTP request type
    if request.form["type"] == "offer":
        # Store the offer in dictionary with key: `offer`
        data["offer"] = {"id" : request.form["id"], "type" : request.form["type"], "sdp": request.form["sdp"]}
        return Response(status=200)
    else:
        return Response(status=400)
    
# 2. Client #2 - Requests/Receives an offer, creates an Answer
@app.route("/answer", methods = ["POST"])
def answer():
    # Check for HTTP request type
    if request.form["type"] == "answer":
        # Store the offer in dictionary with key: `offer`
        data["answer"] = {"id" : request.form["id"], "type" : request.form["type"], "sdp": request.form["sdp"]}
        return Response(status=200)
    else:
        return Response(status=400)

# 3. Client #2 - Sends Answer back
@app.route("/getOffer", methods = ["GET"])
def getOffer():
    if "offer" in data:
        json_object = json.dumps(data["offer"])
        del data["offer"]
        return Response(json_object, status=200, mimetype="application/json")
    else:
        return Response(status=503)

# 4. Client #1 - Receives the Answer
@app.route("/getAnswer", methods = ["GET"])
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