from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=4, description="Password")
    email: EmailStr = Field(..., description="User email")

class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=4, description="Password")

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(None, min_length=4, description="New password (at least 4 characters)")
