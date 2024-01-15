#!/usr/bin/env python3

#
# Copyright (C) 2024 Joelle Maslak
# All Rights Reserved - See License
#

import os
import redis
import subprocess

from celery import Celery, Task, shared_task
from flask import Flask

REDIS = redis.from_url("redis://localhost")

def celery_app_init(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

@shared_task
def process_pdf(prefix):
    dirname = os.path.dirname(prefix)
    filepart = os.path.basename(prefix)
    if not os.path.exists(f"{prefix}.pdf"):
        return
    REDIS.set(f"status-{filepart}", "processing")

    try:
        subprocess.run(["docker", "run", "-it", "--user",
                        f"{os.getuid()}:{os.getgid()}", "-v",
                        f"{dirname}:/usr/pdf", "jmaslak/format-scan-pdf",
                        "--runfile", f"{filepart}.run",
                        f"{filepart}.pdf", f"{filepart}-processed.pdf"], shell=False, check=True)
    except:
        if os.path.exists(f"{prefix}.pdf"):
            os.remove(f"{prefix}.pdf")
        if os.path.exists(f"{prefix}.run"):
            os.remove(f"{prefix}.run")
        if os.path.exists(f"{prefix}-processed.pdf"):
            os.remove(f"{prefix}-processed.pdf")
        REDIS.set(f"after-{filepart}", 0)
        REDIS.delete(f"after-{filepart}")
        REDIS.set(f"status-{filepart}", "errored")
        REDIS.pexpire(f"status-{filepart}", 3_600_000)  # one hour
        REDIS.decr("keysqueued")
        REDIS.pexpire(f"filename-{filepart}", 3_600_000)  # one hour
        raise

    REDIS.set(f"after-{filepart}", 0)
    REDIS.delete(f"after-{filepart}")
    REDIS.set(f"status-{filepart}", "done")
    REDIS.pexpire(f"status-{filepart}", 3_600_000)  # one hour
    REDIS.decr("keysqueued")
    REDIS.pexpire(f"filename-{filepart}", 3_600_000)  # one hour

    if os.path.exists(f"{prefix}.pdf"):
        os.remove(f"{prefix}.pdf")
    if os.path.exists(f"{prefix}.run"):
        os.remove(f"{prefix}.run")
