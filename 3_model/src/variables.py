import os

PORT = os.environ.get("PORT", 5001)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ADAPTER_BUCKET = os.environ["ADAPTER_BUCKET"]
QLORA_ADAPTER_FOLDER = os.environ["QLORA_ADAPTER_FOLDER"]

LOCAL_QLORA_ADAPTER_FOLDER = os.path.join(BASE_DIR, "gen_deps", QLORA_ADAPTER_FOLDER)

USE_7B = os.getenv("LLM_MODEL_PATH", "false") == "true"

USE_INSECURE_CHANNEL = os.getenv("USE_INSECURE_CHANNEL", "false") == "true"
