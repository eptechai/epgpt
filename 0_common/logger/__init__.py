from .logger import create_logger, configure_format
from .variables import ENV

if ENV == "GCP":
    from .gcp import configure_gcp_logging as configure_logging
else:
    raise NotImplementedError(f"PubSub not implemented for environment: {ENV}")
