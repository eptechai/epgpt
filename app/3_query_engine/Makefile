## Definitions
# Directory where the generated Python code should be saved.
OUT_DIR := gen_deps
QUERY_ENGINE_OUT_DIR := $(OUT_DIR)/query_engine_proto

# Directory paths
CURRENT_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(CURRENT_DIR))
COMMON_DIR := $(BASE_DIR)/0_common
PYTHONPATH := $(CURRENT_DIR)/$(OUT_DIR):$(CURRENT_DIR)/$(QUERY_ENGINE_OUT_DIR):$(CURRENT_DIR)/src
DOCKER_IMAGE_NAME := $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

##Scripts and Build Targets
# Installs requirements from pip
setup:
	pip install -r requirements/dev.txt && pip install -r $(COMMON_DIR)/requirements.txt

# Pools all the required dependencies from various directories
generate_deps: all
	@mkdir -p $(OUT_DIR)
	cp -r $(COMMON_DIR)/* $(OUT_DIR)

	@mkdir -p $(QUERY_ENGINE_OUT_DIR)
	cd ../3_query_engine_proto && make all
	cp -r ../3_query_engine_proto/gen_dist/* $(QUERY_ENGINE_OUT_DIR)

# Run the server locally.
run: 
	export PYTHONPATH=$(PYTHONPATH) && cd src && python app.py
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
	docker run -it --rm -p 5003:5003 --net=host -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" ${DOCKER_IMAGE_NAME}:latest

# Deploy to dev
deploy/dev: 
# doppler run --command="dagger run npx ts-node dagger.ts -d local"

## Fundamental build commands.
all: $(OUT_DIR)/embedding-model

# Download the Embedding Model
$(OUT_DIR)/embedding-model:
	@mkdir -p $@

.PHONY: all clean run run/all test build
