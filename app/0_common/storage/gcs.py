import os
from typing import Optional

from google.cloud import storage

from . import variables as vars
from .storage import Storage


class GCS(Storage):
    def __init__(self, bucket) -> None:
        self.bucket_name = bucket
        self.client = storage.Client.from_service_account_info(vars.CREDENTIALS)
        self.bucket = storage.Client.bucket(self.client, self.bucket_name)

    def exists(self, remote_path: str):
        return self.bucket.get_blob(remote_path) is not None

    def exists_or_raise(self, remote_path: str):
        if not self.exists(remote_path):
            raise FileNotFoundError(f"GCS Path: {remote_path} not found")

        return True

    def download_file(self, remote_path: str, local_path: str):
        assert self.exists_or_raise(remote_path)

        blob = self.bucket.blob(remote_path)
        blob.download_to_filename(local_path)

    def upload_file(self, local_path: str, remote_path: str):
        self.bucket.blob(remote_path).upload_from_filename(local_path)

    def upload_file_from_memory(self, data: bytes, remote_path: str):
        blob = self.bucket.blob(remote_path)
        blob.upload_from_string(data)

    def delete_file(self, remote_path: str):
        if self.exists(remote_path):
            self.bucket.blob(remote_path).delete()

    def list_files(self, prefix: Optional[str] = '', only_file_names=True):
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

        if only_file_names:
            return [blob.name for blob in blobs]

        return blobs

    def download_folder(self, remote_path: str, local_path: str):
        blobs = self.list_files(prefix=remote_path, only_file_names=False)

        if not os.path.exists(local_path):
            os.mkdir(local_path)

        for blob in blobs:
            file_path = os.path.join(local_path, os.path.basename(blob.name))
            blob.download_to_filename(file_path)

    def upload_folder(self, local_path: str, remote_path: str):
        for root, _, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(remote_path, file)
                self.upload_file(local_file_path, remote_file_path)

    def delete_folder(self, remote_path: str):
        blobs = self.list_files(prefix=remote_path, only_file_names=False)
        for blob in blobs:
            blob.delete()
