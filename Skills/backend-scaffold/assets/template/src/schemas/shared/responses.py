"""
Shared response schemas.
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Action responses without a resource body (logout, delete, trigger)."""
    message: str
    data: Any | None = None


class DownloadResponse(BaseModel):
    file_byte: str = Field(..., description="Byte content of the file")
    filename: str = Field(..., description="Name of the downloaded file")
    content_type: str = Field(..., description="MIME type of the file")
    message: Optional[str] = Field(None, description="Optional message")
