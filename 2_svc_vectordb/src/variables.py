from os import getenv

# Google Cloud Service Account key for access to Storage Bucket containing FAISS index.
GCP_SVC_APP_KEY = getenv("GCP_SVC_APP_KEY")
if not GCP_SVC_APP_KEY:
    raise ValueError("GCP_SVC_APP_KEY not set.")

# Bucket in which the FAISS index is found.
GCS_VECTORDB_INDEX_GLOBAL_BUCKET = getenv("GCS_VECTORDB_INDEX_GLOBAL_BUCKET")
if not GCS_VECTORDB_INDEX_GLOBAL_BUCKET:
    raise ValueError("GCS_VECTORDB_INDEX_GLOBAL_BUCKET not set.")

# Path to which temporary FAISS index will be downloaded.
FAISS_INDEX_PATH = "/tmp/app/faiss_index"
# Port on which the server will listen.
PORT = getenv("PORT", 5002)
