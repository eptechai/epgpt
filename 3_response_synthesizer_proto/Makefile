## Definitions
# Name of the .proto file without the extension.
PROTO_NAME := response_synthesizer
# Directory where the .proto file resides.
PROTO_DIR := src
# Directory where the generated Python code should be saved.
OUT_DIR := gen_dist

# Installs requirements from pip
setup:
	pip install -r requirements.txt

# Convenience target to run primary build command.
all: $(OUT_DIR)/$(PROTO_NAME)_pb2.py $(OUT_DIR)/$(PROTO_NAME)_pb2_grpc.py

# Compiles protobuf stubs for Python.
$(OUT_DIR)/$(PROTO_NAME)_pb2.py $(OUT_DIR)/$(PROTO_NAME)_pb2_grpc.py: $(PROTO_DIR)/$(PROTO_NAME).proto
	@mkdir -p $(OUT_DIR)
	python -m grpc_tools.protoc -I$(PROTO_DIR) --python_out=$(OUT_DIR) --pyi_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) $<

clean:
	rm -rf $(OUT_DIR)/*

.PHONY: all clean run run/all
