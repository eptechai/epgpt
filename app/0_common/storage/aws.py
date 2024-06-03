import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
import boto3.session

from . import variables as vars
from .storage import Storage


class AWS(Storage):
    def __init__(self, bucket) -> None:
        self.bucket_name = bucket
        self.session = boto3.Session(
            aws_access_key_id=vars.CREDENTIALS["ACCESS_KEY"],
            aws_secret_access_key=vars.CREDENTIALS["SECRET_KEY"]
            )
        self.resource = self.session.resource('s3')
        self.bucket_name = bucket
        self.bucket = self.resource.Bucket(self.bucket_name)

    def exists(self, remote_path: str):
        error = None
        found = False
        try:
            self.resource.Object(self.bucket_name, remote_path).load()
            found = True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                error = "Not Found"
            else:
                error = e.response['Error']['Message']
        return found, error

    def exists_or_raise(self, remote_path: str):
        found, error = self.exists(remote_path)
        if not found:
            raise FileNotFoundError(f"AWS Path: {remote_path} not found. Possible Error {error}")

        return True

    def download_file(self, remote_path: str, local_path: str):
        assert self.exists_or_raise(remote_path)

        self.bucket.download_file(remote_path, local_path)

    def upload_file(self, local_path: str, remote_path: str):
        self.bucket.upload_file(local_path, remote_path)

    def upload_file_from_memory(self, data: bytes, remote_path: str):
        self.resource.Object(self.bucket_namebucket, remote_path).put(Body=data)


    def delete_file(self, remote_path: str):
        if self.exists(remote_path):
             self.resource.Object(self.bucket_name, remote_path).delete()

    def list_files(self, prefix: Optional[str] = '', only_file_names=True):
        objects = self.bucket.objects.filter(Prefix=prefix)
        blobs = []
        if only_file_names:
            for obj in objects:
                if not obj.key.endswith('/'):
                    blobs.append(obj.key)
        else:
            blobs.extend([obj.key for obj in objects])

        return blobs

    def download_folder(self, remote_path: str, local_path: str):
        blobs = self.list_files(prefix=remote_path, only_file_names=True)

        if not os.path.exists(local_path):
            os.mkdir(local_path)

        for blob in blobs:
            file_path = os.path.join(local_path, os.path.basename(blob))
            self.download_file(remote_path, file_path)

    def upload_folder(self, local_path: str, remote_path: str):
        for root, _, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(remote_path, file)
                self.upload_file(local_file_path, remote_file_path)

    def delete_folder(self, remote_path: str):
        blobs = self.list_files(prefix=remote_path, only_file_names=False)
        for blob in blobs:
            self.delete_file(blob)