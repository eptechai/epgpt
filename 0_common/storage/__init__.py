from .variables import ENV

if ENV == "GCP":
    from .gcs import GCS as Storage
else:
    raise NotImplementedError(f"PubSub not implemented for environment: {ENV}")
