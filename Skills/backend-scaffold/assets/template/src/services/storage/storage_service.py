"""
Storage service — boto3 → DigitalOcean Spaces (S3-compatible). All file I/O goes here.
"""
from boto3 import Session
from fastapi import File, UploadFile, HTTPException, status

from configs.settings import settings

_ALLOWED = {"jpg", "jpeg", "png", "pdf", "doc", "docx", "ppt", "pptx", "txt", "csv", "xlsx"}


class StorageService:
    def __init__(self):
        self.session = Session(
            aws_access_key_id=settings.BUCKET_KEY,
            aws_secret_access_key=settings.BUCKET_SECRET,
        )
        self.s3_client = self.session.client(
            "s3", endpoint_url=settings.BUCKET_REGION_ENDPOINT,
        )

    def upload(self, file: UploadFile = File(...)) -> str:
        extension = file.filename.split(".")[-1].lower()
        if extension not in _ALLOWED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="File extension is not supported")
        self.s3_client.upload_fileobj(
            file.file, settings.BUCKET_NAME, file.filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )
        return f"{settings.BUCKET_URL}/{file.filename}"

    def upload_bytes(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        self.s3_client.put_object(
            Bucket=settings.BUCKET_NAME, Key=file_name, Body=file_bytes,
            ACL="public-read", ContentType=content_type,
        )
        return f"{settings.BUCKET_URL}/{file_name}"

    def delete(self, file_url: str) -> None:
        key = file_url.split("/")[-1]
        self.s3_client.delete_object(Bucket=settings.BUCKET_NAME, Key=key)


# Lazily instantiated singleton — created on first import.
storage_service = StorageService()
