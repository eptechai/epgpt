#/bin/bash

# TODO: Avoid unnecessarily generating server keys if use_insecure_channel is set to true.
cd /app/src && gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5050 main:app