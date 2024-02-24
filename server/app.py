import json
import os
from datetime import datetime

import jwt
import requests
from database import JsonData, create_session, setup_database
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

app = Flask(__name__)

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
engine = setup_database()


def default_error_responder(request_limit: RequestLimit):
    abort(401)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://",
    on_breach=default_error_responder,
)


@app.route("/", methods=["GET"])
def index():
    process_request(request)
    return render_template("index.da.html")


@app.route("/en/", methods=["GET"])
def index_en():
    process_request(request)
    return render_template("index.html")


@app.route("/doc/", methods=["GET"])
def index_doc():
    process_request(request)
    return render_template("index.da.usb.html")


@app.route("/doc/en/", methods=["GET"])
def index_doc_en():
    process_request(request)
    return render_template("index.usb.html")


def process_request(request):
    try:
        token = jwt.decode(request.args.get("t"), JWT_SECRET, "HS256")
    except jwt.exceptions.InvalidSignatureError:
        print("INVALID JWT")
        abort(401)
    except jwt.exceptions.DecodeError:
        print("NO JWT")
        abort(401)

    date = datetime.now()
    timestamp = datetime.timestamp(date)
    user_agent = request.headers.get("User-Agent")
    ip = request.headers.get("X-Real-Ip")

    data = {
        "group": token["group"],
        "id": token["id"],
        "filename": token["filename"] if "filename" in token else None,
        "data": {
            "date": str(date),
            "timestamp": str(timestamp),
            "User-Agent": user_agent,
        },
    }

    info = json.loads(requests.get("http://ip-api.com/json/%s" % ip).text)
    del info["query"]
    data["whois"] = info

    print(json.dumps(data, indent=4))
    
    try:
        session = create_session(engine)
        json_data_obj = JsonData(entry=data)
        session.add(json_data_obj)
        session.commit()
        session.close()
        print(jsonify({"message": "JSON data inserted successfully"}))
    except Exception as e:
        print(jsonify({"error": str(e)}))
        abort(401)
