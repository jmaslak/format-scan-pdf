#!/usr/bin/env python3

#
# Copyright (C) 2024 Joelle Maslak
# All Rights Reserved - See License
#

import os
import re
import secrets

import redis

from flask import render_template, redirect, request
from webapp import app, celery_app

import webapp.task as task
from werkzeug.utils import secure_filename

SAVELOC = os.path.expanduser("~/pdf")
MINSIZE = 1000
MAXQUEUE = 5
MBMAX = 200  # 200MB
app.config["MAX_CONTENT_LENGTH"] = MBMAX * 1024 * 1024
REDIS = redis.from_url("redis://localhost")


@app.route("/")
@app.route("/index")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
@app.route("/index", methods=["POST"])
@app.route("/index.html", methods=["POST"])
def index_post():
    if "file" not in request.files:
        return render_template("error.html", errortext=["You must select a PDF file."])

    kq = REDIS.get("keysqueued")
    if kq is not None and int(kq) >= MAXQUEUE:
        return render_template("error.html", errortext=["Server is too busy right now.", "Please try later."])

    invalid = False
    if request.form.get("remove_metadata") not in ("no", "yes"):
        invalid = True
    elif request.form.get("rotate") not in (
        "none",
        "clockwise",
        "anticlockwise",
        "180",
    ):
        invalid = True
    elif request.form.get("crop") not in (
        "100center",
        "90east",
        "80east",
        "90west",
        "80west",
        "80center",
        "60center",
    ):
        invalid = True
    elif request.form.get("split") not in (
        "no",
        "all",
        "skipfirst",
        "skiplast",
        "skipfirstlast",
    ):
        invalid = True
    elif request.form.get("remove_pages") not in ("no", "first", "last", "firstlast"):
        invalid = True
    elif request.form.get("deskew") not in (
        "no",
        "standard",
        "standardskipfirst",
        "100",
        "100skipfirst",
        "200",
        "200skipfirst",
    ):
        invalid = True
    if request.form.get("ocr") not in ("no", "yes"):
        invalid = True

    if invalid:
        return render_template(
            "error.html",
            errortext=[
                "Incorrect form values. If you believe this is an error on the server, please let jmaslak@antelope.net know!"
            ],
        )

    prefix = get_temp_prefix()

    f = request.files["file"]
    fn = f.filename
    f.save(f"{prefix}.pdf")
    filelen = os.stat(f"{prefix}.pdf").st_size
    if filelen == 0:
        return render_template("error.html", errortext=["You must select a PDF file."])
    elif filelen < MINSIZE:
        return render_template(
            "error.html", errortext=["The file seems too small to be a valid PDF file."]
        )

    with open(f"{prefix}.run", "w") as out:
        out.write(f"remove_metadata {request.form.get('remove_metadata')}\n")
        out.write(f"rotate {request.form.get('rotate')}\n")
        out.write(f"crop {request.form.get('crop')}\n")
        out.write(f"split {request.form.get('split')}\n")
        out.write(f"remove_pages {request.form.get('remove_pages')}\n")
        out.write(f"deskew {request.form.get('deskew')}\n")
        out.write(f"ocr {request.form.get('ocr')}\n")

    filepart = os.path.basename(prefix)

    REDIS.set(f"status-{filepart}", "queued")
    REDIS.set(f"filename-{filepart}", fn)
    k = REDIS.get("lastkey")
    if k is not None:
        REDIS.set(f"after-{filepart}", k)
    REDIS.incr("keysqueued")
    REDIS.set("lastkey", filepart)

    task.process_pdf.delay(f"{prefix}")

    return redirect(f"waiting.html?key={filepart}")


@app.route("/waiting.html")
def waiting():
    key = request.args.get("key")
    if key == None:
        return render_template("error.html", errortext=["Missing file key"])

    if not re.search(r"^[A-Za-z0-9_-]+$", key):
        return render_template(
            "error.html",
            errortext=[
                "Invalid file key!",
                "Please be kind. This server is run by a single person, not a corporation.",
            ],
        )

    status = REDIS.get(f"status-{key}")
    if status is not None:
        status = status.decode("utf-8")

    # Handle error!
    if status is None and not os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return render_template(
            "error.html",
            errortext=[
                "You have referenced a file that isn't on the server.",
                "Files are deleted as soon as they are downloaded.",
            ],
        )

    from icecream import ic

    ic(f"{SAVELOC}/{key}")

    if status is None and os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return redirect(f"done.html?key={key}")

    if status == "done" and os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return redirect(f"done.html?key={key}")

    if status == "done" and not os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return render_template(
            "error.html",
            errortext=[
                "You have referenced a file that isn't on the server.",
                "Files are deleted as soon as they are downloaded.",
            ],
        )

    if status == "errored":
        return render_template(
            "error.html",
            errortext=["Sadly, your file could not be processed due to an error."],
        )

    return render_template(
        "waiting.html", prefix=key, pending=get_pending_requests(key), status=status
    )


@app.route("/done.html")
def done():
    key = request.args.get("key")
    if key == None:
        return render_template("error.html", errortext=["Missing file key"])

    if not re.search(r"^[A-Za-z0-9_-]+$", key):
        return render_template(
            "error.html",
            errortext=[
                "Invalid file key!",
                "Please be kind. This server is run by a single person, not a corporation.",
            ],
        )

    return render_template("done.html", key=key)


@app.route("/download")
def download():
    key = request.args.get("key")
    if key == None:
        return render_template("error.html", errortext=["Missing file key"])

    if not re.search(r"^[A-Za-z0-9_-]+$", key):
        return render_template(
            "error.html",
            errortext=[
                "Invalid file key!",
                "Please be kind. This server is run by a single person, not a corporation.",
            ],
        )

    status = REDIS.get(f"status-{key}")
    if status is not None:
        status = status.decode("utf-8")

    fn = REDIS.get(f"filename-{key}")
    if fn is None:
        fn = f"{key}.pdf"
    else:
        fn = fn.decode("utf-8")

    REDIS.set(f"after-{key}", 0)
    REDIS.pexpire(f"status-{key}", 3_600_000)  # One hour
    REDIS.delete(f"status-{key}")
    REDIS.pexpire(f"after-{key}", 3_600_000)  # One hour
    REDIS.delete(f"after-{key}")
    REDIS.pexpire(f"filename-{key}", 3_600_000)  # One hour
    REDIS.delete(f"filename-{key}")

    if status is None and os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return app.response_class(
            stream_and_remove_file(key),
            headers={"Content-Disposition": f"attachment; filename={fn}"},
        )

    if status == "done" and os.path.exists(f"{SAVELOC}/{key}-processed.pdf"):
        return app.response_class(
            stream_and_remove_file(key),
            headers={"Content-Disposition": f"attachment; filename={fn}"},
        )

    return render_template(
        "error.html",
        errortext=[
            "You have referenced a file that isn't on the server.",
            "Files are deleted as soon as they are downloaded.",
        ],
    )

@app.errorhandler(413)
def error_413(e):
    return render_template(
        "error.html",
        errortext=[f"This server is limited to a maximum PDF size of {MBMAX}MB"],
    )


def stream_and_remove_file(key):
    ourfn = f"{SAVELOC}/{key}-processed.pdf"
    fh = open(ourfn, "rb")
    os.remove(ourfn)
    return fh


def get_temp_prefix():
    return f"{SAVELOC}/web-{secrets.token_urlsafe(nbytes=64)}"


def get_pending_requests(key):
    cnt = 0
    k = key
    while k is not None:
        k = REDIS.get(f"after-{k}")
        from icecream import ic

        ic(k)
        if k is not None:
            k = k.decode("utf-8")
        if k is not None and k != "0":
            cnt += 1

    if cnt < 1:
        cnt = 1
    return cnt - 1
