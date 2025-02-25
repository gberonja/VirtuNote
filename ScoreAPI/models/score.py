from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class FileUploadResponse(BaseModel):
    file_url: str
    metadata: Optional[Dict] = Field(
        None,
        example={
            "score_id": "abc123",
            "title": "Moonlight Sonata",
            "composer": "Ludwig van Beethoven"
        }
    )

class FileInfo(BaseModel):
    file_url: str
    metadata: Optional[Dict] = None

class FileListResponse(BaseModel):
    files: List[FileInfo]

class DeleteScoreRequest(BaseModel):
    file_key: str = Field(..., example="user_123/abc123.pdf")
