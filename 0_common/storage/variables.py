import json
import os

BUILD_ENV = os.environ.get("BUILD_ENV", "False").lower() == "true"

if BUILD_ENV is True:
    DEBUG = True
    for env_var in ["CLOUD_STORAGE_CREDENTIALS"]:
        os.environ.setdefault(env_var, "{}")


try:
    ENV = os.environ.get("ENV", "GCP")
    CREDENTIALS = json.loads(os.environ.get("CLOUD_STORAGE_CREDENTIALS"))
except KeyError:
    raise EnvironmentError("Missing environment variable: CLOUD_STORAGE_CREDENTIALS")
