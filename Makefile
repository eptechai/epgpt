## Definitions
HELMCHART_DIR := ./0_helmchart
OUT_DIR := ./generated
SOURCE_DIRS := 0_terraform/dev 0_terraform/stg 1_attachments 1_frontend \
1_backend 2_database 2_svc_vectordb 3_conversation_index 3_model

## Phony Targets
.PHONY: all format $(SOURCE_DIRS)

## App Commands

# Formats source code.
format:
	-@for dir in $(SOURCE_DIRS); do \
		(cd $$dir && $(MAKE) -i format); \
	done

# Create build artifacts (gen_deps, gen_dist) in local folders.
build:
	doppler run --command="dagger run npx ts-node ci.ts -t dev --export-artifacts"

# Uses Dagger to build images to local.
publish/local:
	doppler run --command="dagger run npx ts-node ci.ts -t dev --publish-local"
deploy/local:
	doppler run --command="dagger run npx ts-node ci.ts -t dev --publish-local --deploy-local"

# Publish image to registry.
publish/dev:
	doppler run --command="dagger run npx ts-node ci.ts -t dev --publish"

# Build & deploy everything to dev nomad cluster.
deploy/dev:
	doppler run --command="dagger run node --loader ts-node/esm ci.ts -t dev --publish"

## Dependency Commands
setup:
	pip install -r requirements.txt

docker/images:
	eval $$(minikube docker-env -u) && docker images

clean:
	rm -rf $(OUT_DIR)