## Definitions
# Name of the .proto file without the extension.
PROTO_NAME := vectordb
# Directory where the .proto file resides.
PROTO_DIR := src
# Directory where the generated Python code should be saved.
OUT_DIR := gen_deps
VECTORDB_OUT_DIR := $(OUT_DIR)/svc_vectordb_proto
# Directory where the FAISS index directory resides, for testing.
TEST_FAISS_INDEX_DIR := lfs/test/faiss-index
# Name of the docker image to build.
DOCKER_IMAGE_NAME :=  $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

# PythonPath stuff
CURRENT_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(CURRENT_DIR))
COMMON_DIR := $(BASE_DIR)/0_common
PYTHONPATH := $(CURRENT_DIR)/$(OUT_DIR):$(CURRENT_DIR)/$(VECTORDB_OUT_DIR):$(CURRENT_DIR)/src

## Developer commands
# Installs requirements from pip
setup:
	pip install -r requirements/dev.txt
generate_deps: all
	@mkdir -p $(VECTORDB_OUT_DIR)
	cd ../2_svc_vectordb_proto && make all
	cp -r ../2_svc_vectordb_proto/gen_dist/* $(VECTORDB_OUT_DIR)

	@mkdir -p $(OUT_DIR)/logger
	cp -r $(COMMON_DIR)/logger/* $(OUT_DIR)/logger
lint:
	ruff check src
format:
	black src

## Local execution commands.
# Runs the gRPC server locally.
run:
	export PYTHONPATH=${PYTHONPATH} && cd src && python app.py
run/local: all
	export PYTHONPATH=${PYTHONPATH} && cd src && python app.py
# Tests the gRPC server locally.	
test/local: all
	doppler run --command "pytest -s -rP"

## Docker execution commands
# Build the docker image
build/docker: all
	docker build -t ${DOCKER_IMAGE_NAME}:latest .

run/docker: build/docker
	docker run -it --rm -p 5002:5002 --net=host --entrypoint "doppler" -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" 2_svc_vectordb:latest run --command "python -u app.py"

run/dockerregistry: 
	docker run -it --rm -p 5002:5002 --net=host --entrypoint "doppler" -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" --pull always localhost:5000/svc_vectordb_global:local run --command "python -u app.py"
# docker run -it --rm -p 5002:5002 --net=host -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" --entrypoint "/bin/sh" localhost:5000/svc_vectordb_global:local
stop/docker:
	docker stop $$(docker ps -a -q --filter ancestor=${DOCKER_IMAGE_NAME} --format="{{.ID}}")

## Runs test against a docker container that is started and running locally. You must start the docker container first.
test/docker: build/docker
	pytest -s -rP --endpoint localhost:5001
	
## Kubernetes Execution Commands
build/kube: all
	eval $(minikube docker-env) && docker build -t ${DOCKER_IMAGE_NAME}:latest .

## Fundamental build commands.
all: $(OUT_DIR)/faiss_index $(OUT_DIR)/embedding-model/config.json

# Move FAISS Index from git-lfs to the output directory.
$(OUT_DIR)/faiss_index: 
	@mkdir -p $(OUT_DIR)/faiss_index
	cp -r $(TEST_FAISS_INDEX_DIR)/* $(OUT_DIR)/faiss_index

# Download the Embedding Model
$(OUT_DIR)/embedding-model:
	@mkdir -p $@

$(OUT_DIR)/embedding-model/config.json: $(OUT_DIR)/embedding-model
	huggingface-cli download --local-dir-use-symlinks False --repo-type model BAAI/bge-base-en --local-dir $<

clean:
	rm -rf $(OUT_DIR)/*

.PHONY: all clean run run/all test build $(OUT_DIR)/faiss_index
