#!/usr/bin/env python3

#
# Copyright (C) 2024 Joelle Maslak
# All Rights Reserved - See License
#

import webapp.task as task

from flask import Flask

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    ),
)
celery_app = task.celery_app_init(app)

from webapp import routes
