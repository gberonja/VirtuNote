from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime
import uuid


class Comment(BaseModel):
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScoreBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: Literal["classical", "folk", "pop", "rock"] = "classical"


class ScoreInDB(ScoreBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    file_url: HttpUrl
    datum_unosa: datetime = Field(default_factory=datetime.utcnow)
    komentari: List[Comment] = Field(default_factory=list)
    broj_likeova: int = 0
    likes_by_users: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScoreResponse(ScoreInDB):
    pass


class LikeResponse(BaseModel):
    score_id: str
    broj_likeova: int
    message: str = "Like added successfully"


class DeleteResponse(BaseModel):
    message: str = "Resource deleted successfully"
