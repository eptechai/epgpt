import os

import torch
from transformers import BitsAndBytesConfig

BNB_CONFIG = None
PEFT_MODEL = None
TEMP_DIR = "/tmp"
CONTEXT_WINDOW = 512
PORT = os.environ.get("PORT", 5005)
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
USE_INSECURE_CHANNEL = os.getenv("USE_INSECURE_CHANNEL", "false") == "true"
NO_OF_WORKERS = os.getenv("NO_OF_WORKERS", 2 if DEBUG else 4)

PEFT_MODEL_BUCKET = os.environ["PEFT_MODEL_BUCKET"]
PEFT_MODEL_FOLDER = os.environ["PEFT_MODEL_FOLDER"]
MERGED_INDICES_BUCKET = os.environ["MERGED_INDICES_BUCKET_NAME"]

INDEXING_EMBEDDING_MODEL = "gpt-4-1106-preview"
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-large")
MODEL_ID = os.getenv("MODEL_ID", "MBZUAI/LaMini-GPT-124M")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

if USE_GPU:
    EMBEDDING_MODEL = "BAAI/bge-large-en"
    MODEL_ID = "tiiuae/falcon-40b"
    CONTEXT_WINDOW = 2048

    BNB_CONFIG = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    PEFT_MODEL = os.path.join(BASE_DIR, "gen_deps", PEFT_MODEL_FOLDER)
