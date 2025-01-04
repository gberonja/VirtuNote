from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import dynamodb, TABLE_NAME_USERS

router = APIRouter()

@router.post("/register")
def register_user(username: str, password: str):
    """Endpoint za registraciju novog korisnika."""
    table = dynamodb.Table(TABLE_NAME_USERS)
    
    # Provjera postoji li korisnik
    response = table.get_item(Key={"username": username})
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Spremanje korisnika
    hashed_password = get_password_hash(password)
    user = {"username": username, "password": hashed_password}
    table.put_item(Item=user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(username: str, password: str):
    """Endpoint za prijavu korisnika."""
    table = dynamodb.Table(TABLE_NAME_USERS)
    
    # Dohvat korisnika iz tablice
    response = table.get_item(Key={"username": username})
    user = response.get("Item")
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generiranje JWT tokena
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_my_data(current_user: str = Depends(get_current_user)):
    """Dohvat trenutnog korisnika."""
    return {"username": current_user}