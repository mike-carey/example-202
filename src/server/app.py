import http
import uuid
import logging
import os

from flask import Flask, Response, jsonify
from celery.result import AsyncResult

from server.data import DataLoader
from server.utils import celery_init_app


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)

data = DataLoader()

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
if DEBUG:
    app.debug = True
    logger.setLevel(logging.DEBUG)


@app.route('/healthcheck')
def healthcheck():
    return {"status": "ok"}


@app.route('/load/<string:bucket>', methods=['POST'])
def load(bucket: str):
    job_id = data.queue_job(bucket)
    resp = Response(status=http.client.ACCEPTED, mimetype='application/json', response=jsonify({
        "job": str(job_id),
        "location": f"/data/{job_id}"
    }).data)
    load_data.delay(bucket, str(job_id))
    return resp


@app.route('/data/<string:job_id>')
def get_data(job_id: str):
    result = data.get_data(job_id)
    if result is not None:
        return jsonify(result)
    else:
        return Response(status=http.client.NOT_FOUND)


@celery_app.task
def load_data(bucket: str, job_id: str):
    logger.info("Celery is loading data for bucket %s with job_id %s", bucket, job_id)
    return data.load_data_for_s3(bucket, job_id)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
