import json
import os

BUILD_ENV = os.environ.get("BUILD_ENV", "False").lower() == "true"

if BUILD_ENV is True:
    DEBUG = True
    for env_var in ["CLOUD_STORAGE_CREDENTIALS"]:
        os.environ.setdefault(env_var, "{}")


STORAGE_ENV = os.environ.get("ENV", "GCP")


def load_gcp_credentials():
    return json.loads(os.environ.get("CLOUD_STORAGE_CREDENTIALS"))

def load_aws_credentials():
    return {
        "ACCESS_KEY": os.environ.get("ACCESS_KEY"),
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "SESSION_TOKEN":os.environ.get("SESSION_TOKEN"),
    }

CREDENTIALS_OPTIONS = {
    "GCP": load_gcp_credentials,
    "AWS": load_aws_credentials
}

ENV = os.environ.get("ENV", "AWS")

try:
    CREDENTIALS = CREDENTIALS_OPTIONS[ENV]()
except KeyError:
    raise EnvironmentError("Missing Storage variable", extra={"storage_service": ENV})
