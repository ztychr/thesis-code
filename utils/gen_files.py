from lib.msword import make_canary_msword
from lib.msexcel import make_canary_msexcel
from random import choice
from string import ascii_uppercase, ascii_lowercase
from datetime import datetime
import urllib.parse, os, sys, random, json


#LANG="EN"
LANG = "DA"

base_url = "https://pid.dk/?" if LANG == "DA" else "https://pid.dk/en/?"
#base_url = "http://127.0.0.1:5000/?" if LANG == "DA" else "http://127.0.0.1:5000/en/?"# base_url = ''

typex="single"
#typex="multi"
data = {"ufm": 1}
#qr = {"boeing0": 5}


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

if len(sys.argv) > 1:
    PATH = sys.argv[1]
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
                        params["src"] = "html"
                        params["filename"] = filex
                        url = base_url + urllib.parse.urlencode(params)
                        make_html(filex, folder, url)
                        register_entry_usb(params)
                    elif file_type == "docx":
                        params["src"] = "docx"
                        params["filename"] = filex
                        url = base_url + urllib.parse.urlencode(params).replace(
                            "&", "&amp;"
                        )
                        make_docx(filex, folder, url)
                        register_entry_usb(params)
                    elif file_type == "xlsx":
                        params["src"] = "xlxs"
                        params["filename"] = filex
                        url = base_url + urllib.parse.urlencode(params).replace(
                            "&", "&amp;"
                        )
                        register_entry_usb(params)
                        make_xlsx(filex, folder, url)
                    elif file_type == "pdf":
                        params["src"] = "pdf"
                        params["filename"] = filex
                        url = base_url + urllib.parse.urlencode(params)
                        make_html(filex, folder, url)
                        register_entry_usb(params)
                    print("File", url)


def gen_qr_links(qr, baseurl):
    for group in qr:
        for i in range(qr[group]):
            idx = "".join(choice(ascii_uppercase + ascii_lowercase) for i in range(12))
            params = {"group": group, "id": idx, "src": "qr"}
            url = base_url + urllib.parse.urlencode(params)
            register_entry_qr(params)
            print("QR", url)


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


def register_entry_usb(params):
    if not os.path.exists("../data/entries"):  # and not folder == "Root":
        os.makedirs("../data/entries")
    file_path = "../data/entries/%s.usb.json" % params["group"]

    try:
        with open(file_path, "r") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    entry_id = params["id"]
    if entry_id in existing_data:
        existing_data[entry_id].append(params)
    else:
        existing_data[entry_id] = [params]

    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)


def register_entry_qr(params):
    if not os.path.exists("../data/entries"):  # and not folder == "Root":
        os.makedirs("../data/entries")
    file_path = "../data/entries/%s.qr.json" % params["group"]

    try:
        with open(file_path, "r") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    entry_id = params["id"]
    if entry_id in existing_data:
        existing_data[entry_id].append(params)
    else:
        existing_data[entry_id] = [params]

    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)


def gen_time(sync: bool):
    time = 1687793905 if sync else random.randint(1682942400, 1699876800)
    return time


if __name__ == "__main__":
    gen_usb_files(data, layout, base_url)
    #gen_qr_links(qr, base_url)
