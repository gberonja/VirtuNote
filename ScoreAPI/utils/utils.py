from jose import jwt, JWTError
import httpx
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from jose.exceptions import JWTError
from typing import List

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/users/login")
METADATA_API_URL = "http://metadataapi:8000/metadata/"


async def verify_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401, detail="Token does not contain user data")
        return username
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid or expired token")


async def create_metadata(metadata: dict, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(METADATA_API_URL, json=metadata, headers=headers)
        response.raise_for_status()
        return response.json()


async def update_metadata(score_id: str, updates: dict, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{METADATA_API_URL}?score_id={score_id}", json=updates, headers=headers)
        response.raise_for_status()
        return response.json()


async def delete_metadata(score_id: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{METADATA_API_URL}?score_id={score_id}", headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_metadata(score_id: str = None, user_id: str = None, token: str = None) -> List[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if score_id:
        params["score_id"] = score_id
    if user_id:
        params["user_id"] = user_id

    async with httpx.AsyncClient() as client:
        response = await client.get(METADATA_API_URL, params=params, headers=headers)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()
