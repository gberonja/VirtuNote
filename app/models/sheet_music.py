from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class NoteCreate(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    tags: Optional[str] = "classical"
    file_url: str
    datum_unosa: str  # ISO 8601 format

class NoteResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    tags: str
    file_url: str
    datum_unosa: str
    komentari: Optional[List[dict]] = []
    broj_likeova: Optional[int] = 0
