import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

app = Celery("txwell", broker=broker_url, backend=result_backend)

@app.task
def ingest_nightly():
    # TODO: call data-pipeline/jobs/nightly_snapshots.py
    return {"ok": True}

@app.task
def tiles_nightly():
    # TODO: build PMTiles and upload to storage
    return {"ok": True}