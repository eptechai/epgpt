from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str):
        pass

    @abstractmethod
    def upload_file_from_memory(self, data: bytes, remote_path: str):
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str):
        pass

    @abstractmethod
    def delete_file(self, remote_path: str):
        pass

    @abstractmethod
    def list_files(self, prefix: str, only_file_names=True):
        pass

    @abstractmethod
    def download_folder(self, remote_path: str, local_path: str):
        pass

    @abstractmethod
    def upload_folder(self, local_path: str, remote_path: str):
        pass

    @abstractmethod
    def delete_folder(self, remote_path: str):
        pass
