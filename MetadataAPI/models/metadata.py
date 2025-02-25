from pydantic import BaseModel, Field
from typing import Optional

class MetadataCreate(BaseModel):
    score_id: str = Field(..., description="Unique identifier for the score")
    title: str = Field(..., description="Title of the score")
    composer: str = Field(..., description="Composer's name")

class MetadataResponse(BaseModel):
    score_id: str = Field(..., description="Unique identifier for the score")
    title: str = Field(..., description="Title of the score")
    composer: str = Field(..., description="Composer's name")
    uploaded_at: Optional[str] = Field(None, description="Timestamp when metadata was created")
