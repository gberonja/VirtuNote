from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import create_access_token, verify_password, get_current_user, get_password_hash
from database.database import dynamodb, TABLE_NAME_USERS, get_user_by_username, update_user, get_all_users
from models.user import UserResponse, UserRegister, TokenResponse, UpdateUserRequest
import uuid

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister):
    table = dynamodb.Table(TABLE_NAME_USERS)
    # Check if user exists (by username)
    existing_user = table.get_item(Key={"username": user.username})
    if "Item" in existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    user_data = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    }
    table.put_item(Item=user_data)
    return UserResponse(id=user_data["id"], username=user.username, email=user.email)

@router.post("/login", response_model=TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.get_item(Key={"username": form_data.username})
    stored_user = response.get("Item")
    if not stored_user or not verify_password(form_data.password, stored_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get("/profile")
def get_my_profile(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

@router.delete("/delete-account")
def delete_account(current_user: str = Depends(get_current_user)):
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.get_item(Key={"username": current_user})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="User not found")
    table.delete_item(Key={"username": current_user})
    return {"detail": "Account deleted successfully"}

@router.put("/update", response_model=UserResponse)
def update_account(updates: dict, current_user: str = Depends(get_current_user)):
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.get_item(Key={"username": current_user})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = response["Item"]
    updated_user = update_user(user_data["id"], updates)
    return UserResponse(id=updated_user["id"], username=updated_user["username"], email=updated_user["email"])

@router.get("/list")
def list_users():
    return get_all_users()

