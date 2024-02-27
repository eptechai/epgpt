Fascinating news friends, the GPU Gateway module should now be working. We now use tailscale to connect to our GPUs securely without having to deal with random IPs and ports and unsecured connections.
1. The latest instance of the 3_model image will autoconnect to the gateway and print the IP address to the logs.
2. You take the IP address and copy it into a comma-separated list of such addresses under Doppler's "MODEL_HOSTS" secret.
3. Any instance of 4_gpu_gateway, which is a load balancer (health checks TBD) running with Doppler will read out of the MODEL_HOSTS secret and load balance to all tailscale IP addresses listed in MODEL_HOSTS.
    1. You can run on local by going to the folder and running make run/docker, which will allow you to connect to the GPUs in runpod via localhost:5001.
    2. The backend Kubernetes is now deployed with a GPU Gateway sidecar proxy that allows the backend to also connect to it via localhost:5001. Accordingly, I have reconfigured the SVC_MODEL_HOST secret in Doppler to now connect to "127.0.0.1". (Deployment will be done in 15-20 minutes for this).

## Certificate Authority Key Pair Generation Command (Interactive)
```bash
# Generate Certificate Authority
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out ca.key
openssl req -new -key ca.key -out ca.csr -subj "/O=Teragonia Inc./OU=Engineering/CN=idso2305llms-app-dev-gpuca"
openssl req -x509 -key ca.key -in ca.csr -out ca.crt

# Remove newlines from the certificate and key files
base64 -w0 ca.key > ca.key.base64
base64 -w0 ca.csr > ca.csr.base64
base64 -w0 ca.crt > ca.crt.base64

```