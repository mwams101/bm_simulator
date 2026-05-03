"""
File Storage Service

Handles physical file saving and deletion with a local/cloud abstraction
that mirrors the pattern used in file_readers.py.

Local storage:  saves to  uploads/<job_id>/<uuid>_<original_filename>
Cloud storage:  stub — implement save() / delete() for S3, Azure Blob, GCS, etc.

The UPLOAD_DIR root can be overridden via the UPLOAD_DIR environment variable.
"""

import os
import uuid
from abc import ABC, abstractmethod

from fastapi import HTTPException, UploadFile

from models.uploaded_file import UploadFileType

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

ALLOWED_EXTENSIONS: dict[str, UploadFileType] = {
    "csv": UploadFileType.CSV,
    "xlsx": UploadFileType.EXCEL,
    "xls": UploadFileType.EXCEL,
}


def _resolve_file_type(filename: str) -> UploadFileType:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    file_type = ALLOWED_EXTENSIONS.get(ext)
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed extensions: {list(ALLOWED_EXTENSIONS.keys())}"
        )
    return file_type


class FileStorage(ABC):
    @abstractmethod
    def save(self, job_id: int, file: UploadFile) -> dict:
        """
        Save an uploaded file and return a dict with:
            original_filename, uploaded_filename, file_path, file_type, file_size
        """
        pass

    @abstractmethod
    def delete(self, file_path: str) -> None:
        """Remove a file from storage by its path."""
        pass


class LocalFileStorage(FileStorage):
    def save(self, job_id: int, file: UploadFile) -> dict:
        file_type = _resolve_file_type(file.filename)

        job_dir = os.path.join(UPLOAD_DIR, str(job_id))
        os.makedirs(job_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(job_dir, unique_filename)

        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "original_filename": file.filename,
            "uploaded_filename": unique_filename,
            "file_path": file_path,
            "file_type": file_type,
            "file_size": len(contents),
        }

    def delete(self, file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)


class CloudFileStorage(FileStorage):
    """
    Stub for future cloud storage support (S3, Azure Blob, GCS).

    To implement:
        save()   — upload bytes to bucket, return the remote path/URL
        delete() — call the cloud SDK to remove the object
    """

    def save(self, job_id: int, file: UploadFile) -> dict:
        raise NotImplementedError("Cloud file storage is not yet implemented")

    def delete(self, file_path: str) -> None:
        raise NotImplementedError("Cloud file deletion is not yet implemented")


def get_file_storage(storage_backend: str = "local") -> FileStorage:
    backends = {
        "local": LocalFileStorage,
        "cloud": CloudFileStorage,
    }
    storage_class = backends.get(storage_backend)
    if not storage_class:
        raise ValueError(
            f"Unknown storage backend: '{storage_backend}'. Choose from: {list(backends.keys())}"
        )
    return storage_class()