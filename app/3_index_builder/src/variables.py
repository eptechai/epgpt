import os

PORT = os.environ.get("PORT", 5004)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = "/tmp"
GLOBAL_INDICES_DIR = os.path.join(BASE_DIR, "storage")
TEMP_INDICES_DIR = os.path.join(BASE_DIR, "attachments")
CREATED_INDICES_DIR = os.path.join(BASE_DIR, "indices")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
OPENAI_KEY = os.environ["OPENAI_KEY"]
NO_OF_WORKERS = os.getenv(
    "NO_OF_WORKERS", 2 if os.environ.get("DEBUG", "false").lower() == "true" else 4
)

ATTACHMENT_STATUS_EXCHANGE = os.environ["ATTACHMENT_STATUS_EXCHANGE"]
NEW_ATTACHMENT_QUEUE = os.environ["NEW_ATTACHMENT_QUEUE"]
INDEX_DELETION_QUEUE = os.environ["INDEX_DELETION_QUEUE"]

CONV_INDICES_BUCKET_NAME = os.environ["CONV_INDICES_BUCKET_NAME"]
CORPUS_FILE_BUCKET = os.environ["CORPUS_FILE_BUCKET"]
CORPUS_INDICES_BUCKET = os.environ["CORPUS_INDICES_BUCKET"]
GCS_INDEX_BUILDER_BUCKET = os.environ["GCS_INDEX_BUILDER_BUCKET"]
MERGED_INDICES_BUCKET_NAME = os.environ["MERGED_INDICES_BUCKET_NAME"]

LLM_MODEL_NAME = "gpt-4-1106-preview"
EMBED_MODEL_NAME = "BAAI/bge-large-en"
