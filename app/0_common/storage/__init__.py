from .variables import ENV

if ENV == "GCP":
    from .gcs import GCS as Storage
elif ENV == "AWS":
    from .aws import AWS as Storage
else:
    raise NotImplementedError(f"Storage not implemented for environment: {ENV}")
