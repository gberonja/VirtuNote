from fastapi import APIRouter, HTTPException, Depends, Query
from auth.auth import get_password_hash, verify_password, create_access_token, get_current_user
from database.database import dynamodb, TABLE_NAME_USERS
from models.user import UserResponse, TokenResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(
    username: str = Query(..., min_length=3, max_length=50),
    password: str = Query(..., min_length=4)
):
    """Register a new user with validation."""
    table = dynamodb.Table(TABLE_NAME_USERS)

    # Check if username already exists
    response = table.get_item(Key={"username": username})
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password
    hashed_password = get_password_hash(password)

    # Prepare user data for storage
    user_data = {
        "username": username,
        "password": hashed_password
    }

    # Insert user into the database
    table.put_item(Item=user_data)

    return UserResponse(username=username)

from fastapi import Query

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return a JWT token."""
    table = dynamodb.Table(TABLE_NAME_USERS)

    # Provjeri korisnika u bazi
    response = table.get_item(Key={"username": form_data.username})
    user = response.get("Item")

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Kreiraj JWT token
    access_token = create_access_token(data={"sub": form_data.username})
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get("/me")
def get_my_data(current_user: str = Depends(get_current_user)):
    """Dohvat trenutnog korisnika."""
    return {"username": current_user}