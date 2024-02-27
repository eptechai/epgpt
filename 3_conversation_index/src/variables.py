import os

PORT = os.environ.get("PORT", 5003)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = "/tmp"
SEARCHABLE_INDICES_DIR = os.path.join(BASE_DIR, "search")
TEMP_INDICES_DIR = os.path.join(BASE_DIR, "temp")
CREATED_INDICES_DIR = os.path.join(BASE_DIR, "indices")

ATTACHMENT_STATUS_EXCHANGE = os.environ["ATTACHMENT_STATUS_EXCHANGE"]
CONV_INDICES_BUCKET_NAME = os.environ["CONV_INDICES_BUCKET_NAME"]
NEW_ATTACHMENT_QUEUE = os.environ["NEW_ATTACHMENT_QUEUE"]
INDEX_DELETION_QUEUE = os.environ["INDEX_DELETION_QUEUE"]
NO_OF_WORKERS = os.getenv(
    "NO_OF_WORKERS", 2 if os.environ.get("DEBUG", "false").lower() == "true" else 4
)
