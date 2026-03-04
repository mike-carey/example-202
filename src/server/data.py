import threading
import http
import uuid
import logging

import boto3


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


s3 = boto3.client('s3')


class DataLoader:
    def __init__(self):
        self.semaphore = threading.Semaphore(1)
        self.data = {}


    def queue_job(self, bucket_name: str) -> str:
        job_id = str(uuid.uuid4())
        threading.Thread(target=self.load_data_for_s3, args=(bucket_name, job_id)).start()
        return job_id
    

    def get_data(self, job_id: str) -> dict | None:
        with self.semaphore:
            return self.data.get(job_id)


    def load_data_for_s3(self, bucket_name: str, job_id: str):
        files = []
        logger.info("Fetching objects from S3 bucket %s for job_id %s", bucket_name, job_id)
        response = s3.list_objects_v2(Bucket=bucket_name)
        for obj in response.get('Contents', []):
            files.append(obj['Key'])

        with self.semaphore:
            logger.info("Loading in data for job_id %s", job_id)
            self.data[job_id] = {
                "job_id": job_id,
                "bucket_name": bucket_name,
                "files": files
            }
            return self.data[job_id]
