# Example Flask application using 202 Accepted

## Setup

```bash
direnv allow
pip install .
```

## Setup a redis store

One can run a redis instance via docker:

```bash
REDIS_ID="$(docker run -it --rm -d -p 6379:6379 redis:7.2.3)"
```

## Configuring env vars

Configurable environment variables can be found in `.env`.

## Running the server

```bash
python3 -m server.app
```

## Load the data in

```bash
S3_BUCKET='<example-bucket-name>'
curl -iX POST "http://$HOST:$PORT/load/$S3_BUCKET"
```

The response will be a 202 and include a job_id and endpoint to track the data when it is ready.

```json
{
  "job_id": "<job-id>",
  "location": "/data/<job-id>"
}
```

## Get the results

Hit the URL until a 200 is provided.

```bash
curl -i "http://$HOST:$PORT/data/$JOB_ID"
```

## Shutdown

Hit `CTRL+C` to kill the python process.

Stop the redis server:

```bash
docker stop "$REDIS_ID"
```
