import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTACHMENT_DOWNLOAD_PATH = os.path.join(BASE_DIR, "attachments")
DOCUMENTS_DOWNLOAD_PATH = os.path.join(BASE_DIR, "documents")
BUILD_ENV = os.environ.get("BUILD_ENV", "False").lower() == "true"

if BUILD_ENV is True:
    DEBUG = True
    for env_var in [
        "INDEX_BUILDER_SERVICE_HOST",
        "QUERY_ENGINE_SERVICE_HOST",
        "RESPONSE_SYNTHESIZER_SERVICE_HOST",
        "OPENAI_KEY",
        "USER_FILES_BUCKET",
        "NEW_ATTACHMENT_QUEUE",
        "ATTACHMENT_STATUS_EXCHANGE",
        "AUTH_0_CLIENT_ID",
        "AUTH_0_USER_INFO_URL",
        "AUTH_0_JWKS_URL",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "INDEX_DELETION_QUEUE",
    ]:
        os.environ.setdefault(env_var, "")

try:
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    INDEX_BUILDER_SERVICE_HOST = os.environ.get("INDEX_BUILDER_SERVICE_HOST")
    QUERY_ENGINE_SERVICE_HOST = os.environ.get("QUERY_ENGINE_SERVICE_HOST")
    RESPONSE_SYNTHESIZER_SERVICE_HOST = os.environ.get("RESPONSE_SYNTHESIZER_SERVICE_HOST", "127.0.0.1:5006")
    RESPONSE_SYNTHESIZER_API_HOST = os.environ.get("RESPONSE_SYNTHESIZER_API_HOST", "http://response_synthesyzer:5050")
    OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
    USER_FILES_BUCKET = os.environ.get("USER_FILES_BUCKET")
    NEW_ATTACHMENT_QUEUE = os.environ.get("NEW_ATTACHMENT_QUEUE")
    ATTACHMENT_STATUS_EXCHANGE = os.environ.get("ATTACHMENT_STATUS_EXCHANGE")
    AUTH_0_CLIENT_ID = os.environ.get("AUTH_0_CLIENT_ID")
    AUTH_0_USER_INFO_URL = os.environ.get("AUTH_0_USER_INFO_URL")
    AUTH_0_JWKS_URL = os.environ.get("AUTH_0_JWKS_URL")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    INDEX_DELETION_QUEUE = os.environ.get("INDEX_DELETION_QUEUE")
    USE_INSECURE_CHANNEL = os.environ.get("USE_INSECURE_CHANNEL", "True").lower() == "true"
    SUB_QUESTION_MODEL_NAME = os.environ.get("SUB_QUESTION_MODEL_NAME", "gpt-4-1106-preview")
except KeyError as exc:
    raise EnvironmentError(f"Required environment variable: {exc} not found")
