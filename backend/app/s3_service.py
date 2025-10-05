import boto3
import uuid
from typing import Optional
from fastapi import UploadFile
from .config import settings

class S3Service:
    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            # Configure for MinIO
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=getattr(settings, 'S3_ENDPOINT_URL', None)
            )
            # Create bucket if it doesn't exist
            self._ensure_bucket_exists()
        else:
            # Fallback to local storage if S3 credentials not provided
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """Ensure S3 bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=settings.S3_BUCKET)
        except:
            # Bucket doesn't exist, create it
            self.s3_client.create_bucket(Bucket=settings.S3_BUCKET)
    
    async def upload_file(self, file: UploadFile, folder: str = "photos") -> str:
        """Upload file to S3 or local storage"""
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        if self.s3_client:
            # Upload to S3
            try:
                file_content = await file.read()
                self.s3_client.put_object(
                    Bucket=settings.S3_BUCKET,
                    Key=unique_filename,
                    Body=file_content,
                    ContentType=file.content_type
                )
                # Return MinIO URL (use external URL for frontend access)
                endpoint_url = getattr(settings, 'S3_ENDPOINT_URL', None)
                if endpoint_url:
                    # Replace internal Docker URL with external URL
                    external_url = endpoint_url.replace('http://minio:9000', 'http://localhost:9000')
                    return f"{external_url}/{settings.S3_BUCKET}/{unique_filename}"
                else:
                    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            except Exception as e:
                print(f"S3 upload failed: {e}")
                # Fallback to local storage
                return await self._upload_local(file, unique_filename)
        else:
            # Upload to local storage
            return await self._upload_local(file, unique_filename)
    
    async def _upload_local(self, file: UploadFile, filename: str) -> str:
        """Upload file to local storage"""
        import os
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return f"/uploads/{filename}"

s3_service = S3Service()



