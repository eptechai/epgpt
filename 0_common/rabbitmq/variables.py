import os

BUILD_ENV = os.environ.get("BUILD_ENV", "False").lower() == "true"

if BUILD_ENV is True:
    DEBUG = True
    for env_var in [
        "RABBITMQHOST",
        "RABBITMQ_USERNAME",
        "RABBITMQ_PASSWORD",
    ]:
        os.environ.setdefault(env_var, "")

try:
    RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
    RABBITMQ_HOST = os.environ.get("RABBITMQHOST")
    RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
    RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
except KeyError as exc:
    raise EnvironmentError(f"Missing environment variable: {exc}")
