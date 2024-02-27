DOCKER_IMAGE_NAME := $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))
CURRENT_DIR := $(shell pwd)
PYTHONPATH := $(CURRENT_DIR)/src

run:
	cd src && envoy -c envoy.yaml -l debug

.PHONY: test
test:
	export PYTHONPATH=${PYTHONPATH} && pytest -s -rP

build/docker:
	cd src && docker build -t ${DOCKER_IMAGE_NAME}:latest .

run/docker: build/docker
	cd src && docker run --rm -p 5001:5001 --entrypoint "doppler" -e DOPPLER_TOKEN="$$(doppler configs tokens create docker --max-age 1m --plain)" ${DOCKER_IMAGE_NAME}:latest run --command "/home/envoy/startup.sh"