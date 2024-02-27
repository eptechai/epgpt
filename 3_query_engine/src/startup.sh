#/bin/bash

# TODO: Avoid unnecessarily generating server keys if use_insecure_channel is set to true.
cd /root && \
echo $GPU_CA_CERT_B64 | base64 --decode > ca.crt && \
cat ca.crt && \
echo $GPU_CA_KEY_B64 | base64 --decode > ca.key && \
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out server.key && \
openssl req -new -key server.key -out server.csr -subj "/CN=Client" -reqexts SAN -config <(echo -e "[SAN]\nsubjectAltName=IP:$HOST") && \
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -copy_extensions copyall && \
cd /app/src && python -u app.py