import os

import torch
from transformers import BitsAndBytesConfig
from pathlib import Path

from sqlalchemy import make_url

CUR_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

RESPONSE_SYNTHESIZER_API_HOST = os.environ.get("RESPONSE_SYNTHESIZER_API_HOST", "http://localhost:5050")

BNB_CONFIG = None
CONTEXT_WINDOW = 512
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
PORT = os.environ.get("PORT", 5006)
TEXT_FINAL_PROMPT_TMPL = "{context_str}" "---" "{query_str}"


DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
NO_OF_WORKERS = os.getenv("NO_OF_WORKERS", 2 if DEBUG else 4)

MODEL_ID = os.getenv("MODEL_ID", "MBZUAI/LaMini-GPT-124M")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

SIMILARITY_TOP_K = os.getenv("SIMILARITY_TOP_K", 4)
SIMILARITY_CUTOFF = os.getenv("SIMILARITY_CUTOFF", 0.5)
USE_AUTO_RETRIEVER = os.getenv("USE_AUTO_RETRIEVER", "false").lower() == "true"

DBNAME = os.getenv("DBNAME", "vectordb")
PG_CONN_STR = os.getenv("PG_CONNECTION_URL", "postgresql://testuser:testpwd@127.0.0.1:5432")
APG_CONN_STR = ""
PG_URL = make_url(PG_CONN_STR)
PG_CONNECTION_DICT = {
    'dbname': DBNAME,
    'user': PG_URL.username,
    'password': PG_URL.password,
    'host': PG_URL.host,
}

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
