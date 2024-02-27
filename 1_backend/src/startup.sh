#/bin/bash

# TODO: Avoid unnecessarily generating server keys if use_insecure_channel is set to true.
cd /root && \
echo $GPU_CA_CERT_B64 | base64 --decode > ca.crt && \
cat ca.crt && \
echo $GPU_CA_KEY_B64 | base64 --decode > ca.key && \
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out client.key && \
openssl req -new -key client.key -out client.csr -subj "/CN=Client" && \
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt && \
cd /app/src && bash -c "bash attachment_processor.sh &" && gunicorn -k uvicorn.workers.UvicornWorker app:app -c ../config/prod.py
