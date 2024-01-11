from flask import Flask, request, render_template, send_file, abort
from urllib.parse import urlparse
from datetime import datetime
import json, requests, os
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

app = Flask(__name__)


def default_error_responder(request_limit: RequestLimit):
    abort(401)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per hour"],
    storage_uri="memory://",
    on_breach=default_error_responder,
)


@app.route("/", methods=["GET"])
def index():
    process_request(request)
    return render_template("index.da.html")


@app.route("/en/", methods=["GET"])
def index_da():
    process_request(request)
    return render_template("index.html")



def process_request(request):
    date = datetime.now()
    timestamp = datetime.timestamp(date)
    user_agent = request.headers.get("User-Agent")
    ip = request.headers.get("X-Real-Ip")
    src = request.args.get("src")
    group = request.args.get("group")
    idx = request.args.get("id")
    typex = request.args.get("type")
    filename = request.args.get("filename")
    
    try:
        src = src.strip("\\")
        group = group.strip("\\")
        idx = idx.strip("\\")
        typex = typex.strip("\\")
        filename = filename.strip("\\")
    except AttributeError:
        pass
    except Exception as e:
        print(e)

    data = {
        "group": group,
        "id": idx,
        "src": src,
        "type": typex,
        "filename": filename,
        "data": {
            "date": str(date),
            "timestamp": str(timestamp),
            "User-Agent": user_agent,
        },
    }
    
    if src == "qr":
        if not check_entry_qr(group, idx, src):
            fault_file = "data/faults/faults.%s.qr.json" % group
            register_fault(data, fault_file)
            abort(401)
    else:
        if not check_entry_usb(group, idx, src, filename, typex):
            fault_file = "data/faults/faults.%s.usb.json" % group
            register_fault(data, fault_file)
            abort(401)

    info = json.loads(requests.get("http://ip-api.com/json/%s" % ip).text)
    del info['query']
    data["whois"] = info

    if not os.path.exists("data/results"):
        os.makedirs("data/results")

    if src == "qr":
        file_path = "data/results/%s.qr.json" % group
    else:
        file_path = "data/results/%s.usb.json" % group

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {group: []}
        
    existing_data[group].append(data)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)
#    print(json.dumps(data, indent=2))


def check_entry_usb(group, idx, src, filename, typex):
    try:
        with open("data/entries/%s.usb.json" % group, "r") as f:
            entries = json.load(f)
    except FileNotFoundError:
        return abort(401)

    if idx in entries:
        for entry in entries[idx]:
            if (
                entry.get("group") == group
                and entry.get("src") == src
                and entry.get("filename") == filename
                and entry.get("type") == typex
            ):
                print("Entry OK")
                return True

    print("Entry NOT OK")
    return False


def check_entry_qr(group, idx, src):
    try:
        with open("data/entries/%s.qr.json" % group, "r") as f:
            entries = json.load(f)
    except FileNotFoundError:
        return abort(401)

    if idx in entries:
        for entry in entries[idx]:
            if entry.get("group") == group and entry.get("src") == src:
                print("Entry OK")
                return True

    print("Entry NOT OK")
    return False


def register_fault(data, fault_file):
    if not os.path.exists("data/faults"):
        os.makedirs("data/faults")
    with open(fault_file, "a", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


"""    
    if src == "qr":
        with open('data/%s.qr.json' % group, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open('data/%s.drive.json' % group, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    return render_template("index.da.html")
"""
