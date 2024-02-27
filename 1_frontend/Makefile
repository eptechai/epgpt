OUT_DIR := gen_deps
GENERATED_CLIENT_DIR := ./src/generated/client
DOCKER_IMAGE_NAME :=  $(notdir $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST))))))

.PHONY: setup
setup:
	pnpm install


.PHONY: run
run:
	doppler run -- pnpm dev
	

.PHONY: ci
ci:
	pnpm format
	pnpm lint --fix


.PHONY: build
build:
	doppler run -- pnpm build


.PHONY: prod/run
prod/run:
	doppler run -- node build


.PHONY: build/docker
build/docker:
	docker build -t ${DOCKER_IMAGE_NAME}:latest .


.PHONY: run/docker
run/docker: build/docker
	docker run -it --rm -p 3000:3000 ${DOCKER_IMAGE_NAME}:latest


.PHONY: generate_deps
generate_deps:
	@mkdir -p $(OUT_DIR)
	@mkdir -p $(GENERATED_CLIENT_DIR)

	pnpm openapi --input ${OUT_DIR}/openapi.json --output $(GENERATED_CLIENT_DIR) --name FastAPIClient
