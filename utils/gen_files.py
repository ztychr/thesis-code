import os
import random
import sys
from random import choice
from string import ascii_lowercase, ascii_uppercase

import jwt
from dotenv import load_dotenv
from lib.msexcel import make_canary_msexcel
from lib.msword import make_canary_msword

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

LANG = "DA" # or "EN"

# base_url = "https://pid.dk/?t=" if LANG == "DA" else "https://pid.dk/en/?t="
base_url = (
    "http://127.0.0.1:5000/?t=" if LANG == "DA" else "http://127.0.0.1:5000/en/?t="
)

typex = "single" # or "multi"

data = {"group_name": 1}
qr = {"group_name": 1}

layout = {
    "Sommer 2023": [
        "IMG_2622.jpg",
        "IMG_2623.jpg",
        "IMG_2624.jpg",
        "IMG_2625.jpg",
        "IMG_2626.jpg",
        "IMG_2627.jpg",
        "IMG_2628.jpg",
        "IMG_2629.jpg",
        "IMG_2630.jpg",
        "IMG_2631.jpg",
    ],
    "Vigtige Dokumenter": [
        "Mødenoter.docx",
        "Udkast-til-lønsammensætning.docx",
        "Ansættelsesbrev.docx",
        "Budget.xlsx",
        "Afdrag-2024.xlsx",
        "CV.docx",
        "GF-referat.docx",
        "AB-nøgletal.xlsx",
        "MUS-forberedelse.docx",
    ],
}

if len(sys.argv) > 2:
    PATH = sys.argv[2]
else:
    PATH = "output"


def gen_usb_files(data, layout, base_url):
    for group in data:
        for i in range(data[group]):
            idx = "".join(choice(ascii_uppercase + ascii_lowercase) for i in range(12))
            params = {"group": group, "id": idx, "type": typex}

            for folder in layout:
                if not os.path.exists("%s/%s" % (PATH, folder)):
                    os.makedirs("%s/%s" % (PATH, folder))
                    time = gen_time(sync=False)
                    os.utime("%s/%s" % (PATH, folder), (time, time))

                for filex in layout[folder]:
                    file_type = filex.rsplit(".", 1)[-1]
                    if file_type == "jpg":
                        params["filename"] = filex
                        token = jwt.encode(params, JWT_SECRET, algorithm="HS256")
                        url = base_url + token
                        make_html(filex, folder, url)
                    elif file_type == "docx":
                        params["filename"] = filex
                        token = jwt.encode(params, JWT_SECRET, algorithm="HS256")
                        url = base_url + token
                        make_docx(filex, folder, url)
                    elif file_type == "xlsx":
                        params["filename"] = filex
                        token = jwt.encode(params, JWT_SECRET, algorithm="HS256")
                        url = base_url + token
                        make_xlsx(filex, folder, url)
                    elif file_type == "pdf":
                        params["filename"] = filex
                        token = jwt.encode(params, JWT_SECRET, algorithm="HS256")
                        url = base_url + token
                        make_html(filex, folder, url)
                    print(params["filename"], "\n", url)


def gen_qr_links(qr, baseurl):
    for group in qr:
        for i in range(qr[group]):
            idx = "".join(choice(ascii_uppercase + ascii_lowercase) for i in range(12))
            params = {"group": group, "id": idx, "filename": "qr"}
            token = jwt.encode(params, JWT_SECRET, algorithm="HS256")
            url = base_url + token
            print("QR\n", url)


def make_html(file_name, folder, url):
    template = "templates/index.da.html" if LANG == "DA" else "templates/index.html"
    with open(template, "r") as f:
        data = f.read()
        data = data.replace("REPLACE", url)
    with open("%s/%s/%s.html" % (PATH, folder, file_name), "w") as file:
        file.write(data)
    time = gen_time(sync=True) if ".jpg" in file_name else gen_time(sync=False)
    os.utime(file.name, (time, time))


def make_docx(file_name, folder, url):
    with open("%s/%s/%s" % (PATH, folder, file_name), "wb") as f:
        f.write(
            make_canary_msword(
                url=url,
                template="templates/template.da.docx"
                if LANG == "DA"
                else "templates/template.docx",
            )
        )
    time = gen_time(sync=False)
    os.utime(f.name, (time, time))


def make_xlsx(file_name, folder, url):
    with open("%s/%s/%s" % (PATH, folder, file_name), "wb") as f:
        f.write(
            make_canary_msexcel(
                url=url,
                template="templates/template.da.xlsx"
                if LANG == "DA"
                else "templates/template.xlsx",
            )
        )
    time = gen_time(sync=False)
    os.utime(f.name, (time, time))


def gen_time(sync: bool):
    time = 1687793905 if sync else random.randint(1682942400, 1699876800)
    return time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gen-files.py <usb|qr> <path>")
        sys.exit(0)
    if sys.argv[1] == "usb":
        gen_usb_files(data, layout, base_url)
    elif sys.argv[1] == "qr":
        gen_qr_links(qr, base_url)
    else:
        print("Usage: gen-files.py <usb|qr> <path>")
