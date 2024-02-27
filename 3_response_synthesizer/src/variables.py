import os

import torch
from transformers import BitsAndBytesConfig

BNB_CONFIG = None
CONTEXT_WINDOW = 512
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
PORT = os.environ.get("PORT", 5006)
TEXT_FINAL_PROMPT_TMPL = "{context_str}" "---" "{query_str}"

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
NO_OF_WORKERS = os.getenv("NO_OF_WORKERS", 2 if DEBUG else 4)

MODEL_ID = os.getenv("MODEL_ID", "MBZUAI/LaMini-GPT-124M")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

if USE_GPU:
    CONTEXT_WINDOW = 2048
    EMBEDDING_MODEL = "BAAI/bge-large-en"
    MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
    BNB_CONFIG = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
