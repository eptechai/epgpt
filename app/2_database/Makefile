## Definitions
# Directory where the backend logic resides.
CURRENT_DIR := $(shell pwd)
OUT_DIR := $(CURRENT_DIR)/gen_dist
BASE_DIR := $(shell dirname $(CURRENT_DIR))

all:
	prisma generate
seed:
	python seed.py

## Proxies to connect to Cloud SQL in Google Cloud.
# Run "gcloud auth application-default login" to get credentials to access them. 
# Note: Your connection string still needs the password. 

# Connects to the GCP dev environment Cloud SQL on port 5433.
.PHONY: proxy/dev
proxy/dev: ./gen_deps/cloud-sql-proxy
	./gen_deps/cloud-sql-proxy --address 0.0.0.0 --port 5433 trg-d-i0523dsollms-chatapp:us-central1:trg-d-i0523dsollms-chatapp-postgres

# Downloads the cloud-sql-proxy binary
./gen_deps/cloud-sql-proxy:
	mkdir -p ./gen_deps
	curl -o ./gen_deps/cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.7.0/cloud-sql-proxy.linux.amd64
	chmod +x ./gen_deps/cloud-sql-proxy
