## Definitions
# Directory where the generated Python code should be saved.
OUT_DIR := gen_deps
RESPONSE_OUT_DIR := $(OUT_DIR)/response_synthesizer_proto

# Directory paths
CURRENT_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(CURRENT_DIR))
COMMON_DIR := $(BASE_DIR)/0_common
PYTHONPATH := $(CURRENT_DIR)/$(OUT_DIR):$(CURRENT_DIR)/$(RESPONSE_OUT_DIR):$(CURRENT_DIR)/src
DOCKER_IMAGE_NAME := $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

##Scripts and Build Targets
# Installs requirements from pip
setup:
	pip install -r requirements/dev.txt && pip install -r $(COMMON_DIR)/requirements.txt

# Pools all the required dependencies from various directories
generate_deps: all
	@mkdir -p $(OUT_DIR)
	cp -r $(COMMON_DIR)/* $(OUT_DIR)

	@mkdir -p $(RESPONSE_OUT_DIR)
	cd ../3_response_synthesizer_proto && make all
	cp -r ../3_response_synthesizer_proto/gen_dist/* $(RESPONSE_OUT_DIR)

# Run the server locally.
run: 
	export PYTHONPATH=$(PYTHONPATH) && gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5050 src.main:app --timeout 90
run/vector: 
	export PYTHONPATH=$(PYTHONPATH) && cd src/vector_stores/lead_gen && python -m lead_gen_vector_store
run/background:
	export PYTHONPATH=$(PYTHONPATH) && cd src && python indexing_task.py
test: 
	doppler run --command "export RABBITMQHOST=$(RABBITMQ_HOST) && export PYTHONPATH=$(PYTHONPATH) && pytest -s -rP"
lint:
	ruff check src
format:
	black src --line-length 110
clean:
	rm -rf $(OUT_DIR)/*

# Docker related commands
build/docker: 
	docker build -t ${DOCKER_IMAGE_NAME}:latest .
run/docker: build/docker
	docker run -it --rm -p 5050:5050 --net=host ${DOCKER_IMAGE_NAME}:latest

# Deploy to dev
deploy/dev: 
# doppler run --command="dagger run npx ts-node dagger.ts -d local"

## Fundamental build commands.
all: $(OUT_DIR)/embedding-model

# Download the Embedding Model
$(OUT_DIR)/embedding-model:
	@mkdir -p $@


.PHONY: all clean run run/all test build
