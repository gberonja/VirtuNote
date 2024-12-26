from pydantic import BaseModel
from typing import List

class Note(BaseModel):
    korisnik: int
    datum_unosa: str
    url: str
    broj_likeova: int = 0
    komentari: List[str]=[]