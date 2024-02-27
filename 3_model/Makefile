## Definitions
# Directory where the generated Python code should be saved.
OUT_DIR := gen_deps
MODEL_OUT_DIR := $(OUT_DIR)/model_proto

# Directory paths
CURRENT_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(CURRENT_DIR))
COMMON_DIR := $(BASE_DIR)/0_common
PYTHONPATH := $(COMMON_DIR):$(CURRENT_DIR)/$(OUT_DIR):$(CURRENT_DIR)/$(MODEL_OUT_DIR):$(CURRENT_DIR)/src
DOCKER_IMAGE_NAME := $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

##Scripts and Build Targets
# Installs requirements from pip
setup:
	pip install -r requirements/dev.txt && pip install -r $(COMMON_DIR)/requirements.txt

# Pools all the required dependencies from various directories
generate_deps:
	@mkdir -p $(OUT_DIR)
	cp -r $(COMMON_DIR)/* $(OUT_DIR)

	@mkdir -p $(MODEL_OUT_DIR)
	cd ../3_model_proto && make all
	cp -r ../3_model_proto/gen_dist/* $(MODEL_OUT_DIR)

# Runs the gRPC server locally.
run: 
	export PYTHONPATH=$(PYTHONPATH) && cd src && python app.py
test: # Unit Tests
	doppler run --command "export PYTHONPATH=$(PYTHONPATH) && pytest -s -rP test/unit"
.PHONY: test/intg
test/intg: # Integration tests using a real server.
	doppler run --command "export PYTHONPATH=$(PYTHONPATH) && pytest -s -rP test/intg"
lint:
	ruff check src
format:
	black src
clean:
	rm -rf $(OUT_DIR)/*

# Docker related commands
# Build the docker image
build/docker: all
	docker build -t ${DOCKER_IMAGE_NAME}:latest .

# Run the docker image after building it.
run/docker: build/docker
	docker run -it --rm -p 5001:5001 -e DOPPLER_TOKEN=$$(doppler configs tokens create ephemeral-token --max-age 1m --plain) ${DOCKER_IMAGE_NAME}:latest

.PHONY: all clean run run/all test build
