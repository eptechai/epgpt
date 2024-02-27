## Definitions
# Directory where the generated Python code should be saved.
OUT_DIR := gen_deps
DB_OUT_DIR := $(OUT_DIR)/db
MODEL_OUT_DIR := $(OUT_DIR)/model_proto
ATTACHMENT_OUT_DIR := $(OUT_DIR)/attachment_proto
GLOBAL_INDEX_OUT_DIR := $(OUT_DIR)/svc_vectordb_proto
CONVO_INDEX_OUT_DIR := $(OUT_DIR)/conversation_index_proto
INDEX_BUILDER_OUT_DIR := $(OUT_DIR)/index_builder_proto
QUERY_ENGINE_OUT_DIR := $(OUT_DIR)/query_engine_proto
RESPONSE_OUT_DIR := $(OUT_DIR)/response_synthesizer_proto

# Directory paths
CURRENT_DIR := $(shell pwd)
BASE_DIR := $(shell dirname $(CURRENT_DIR))
COMMON_DIR := $(BASE_DIR)/0_common
PYTHONPATH := $(COMMON_DIR):$(CURRENT_DIR)/$(OUT_DIR):$(CURRENT_DIR)/$(DB_OUT_DIR):$(CURRENT_DIR)/$(MODEL_OUT_DIR):$(CURRENT_DIR)/$(ATTACHMENT_OUT_DIR):$(CURRENT_DIR)/$(GLOBAL_INDEX_OUT_DIR):$(CURRENT_DIR)/$(CONVO_INDEX_OUT_DIR):$(CURRENT_DIR)/src:$(CURRENT_DIR)/config:$(CURRENT_DIR)/$(INDEX_BUILDER_OUT_DIR):$(CURRENT_DIR)/$(QUERY_ENGINE_OUT_DIR):$(CURRENT_DIR)/$(RESPONSE_OUT_DIR)
DOCKER_IMAGE_NAME := $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

##Scripts and Build Targets
# Installs requirements from pip
setup:
	pip install -r ${BASE_DIR}/requirements.txt

generate_deps:
	@mkdir -p $(OUT_DIR)
	cp -r $(COMMON_DIR)/* $(OUT_DIR)

	@mkdir -p $(DB_OUT_DIR)
	cd ../2_database && make all
	cp -r ../2_database/gen_dist/* $(DB_OUT_DIR)

	@mkdir -p $(ATTACHMENT_OUT_DIR)
	cd ../1_attachment_proto && make all
	cp -r ../1_attachment_proto/gen_dist/* $(ATTACHMENT_OUT_DIR)

	@mkdir -p $(INDEX_BUILDER_OUT_DIR)
	cd ../3_index_builder && make generate_deps
	cp -r ../3_index_builder_proto/gen_dist/* $(INDEX_BUILDER_OUT_DIR)

	@mkdir -p $(QUERY_ENGINE_OUT_DIR)
	cd ../3_query_engine && make generate_deps
	cp -r ../3_query_engine_proto/gen_dist/* $(QUERY_ENGINE_OUT_DIR)

	@mkdir -p $(RESPONSE_OUT_DIR)
	cd ../3_response_synthesizer && make generate_deps
	cp -r ../3_response_synthesizer_proto/gen_dist/* $(RESPONSE_OUT_DIR)

run/vectordb:
	cd ../2_svc_vectordb && make run
run/model:
	cd ../3_model && make run
run/convo_index:
	cd ../3_conversation_index && make run
run/local: 
	export PYTHONPATH=$(PYTHONPATH) && cd src && uvicorn app:app --reload --host=0.0.0.0 --port=8000
run/bg: 
	export PYTHONPATH=$(PYTHONPATH) && cd src && python process_attachment_status.py
run: 
	export PYTHONPATH=$(PYTHONPATH) && cd src && gunicorn -k uvicorn.workers.UvicornWorker app:app -c ../config/prod.py
test:
	export PYTHONPATH=$(PYTHONPATH) && cd test && doppler run --command "pytest -s -rP"
build:
	export PYTHONPATH=$(PYTHONPATH) && export BUILD_ENV=True && cd build_scripts && python gen_openapi.py
lint:
	ruff check src
format:
	black src

# Docker related commands
build/docker:
	docker build -t ${DOCKER_IMAGE_NAME}:latest .
run/docker: build/docker
	docker run -p 8000:8000 --net=host -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" ${DOCKER_IMAGE_NAME}:latest

.PHONY: test
