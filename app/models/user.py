from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    """Model za registraciju korisnika."""
    username: str
    password: str

class UserResponse(BaseModel):
    """Model za odgovor sa podacima korisnika."""
    username: str

class TokenResponse(BaseModel):
    """Model za odgovor sa tokenom."""
    access_token: str
    token_type: str
    
class LoginRequest(BaseModel):
    username: str
    password: str
