# Requirements

You must have redis installed.

Celery, in a single-task worker config, should have a worker running
like:

```celery -A webapp.celery_app worker --concurrency=1 --loglevel INFO```
