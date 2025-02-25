from jose import jwt, JWTError
import httpx
from fastapi import HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from jose.exceptions import JWTError

# Configuration
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
METADATA_API_URL = "http://127.0.0.1:8002/metadata"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/users/login")

async def verify_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token ne sadrži korisničke podatke")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")

async def create_or_update_metadata(score_id: str, user_id: str, title: str, composer: str):
    metadata = {
        "score_id": score_id,
        "user_id": user_id,
        "title": title,
        "composer": composer
    }
    
    print(f"Sending metadata: {metadata}")  # Debug ispis

    try:
        async with httpx.AsyncClient() as client:
            check_response = await client.get(f"{METADATA_API_URL}?score_id={score_id}")
            print(f"Metadata check response: {check_response.status_code}")  # Debug ispis

            if check_response.status_code == 200:
                response = await client.put(f"{METADATA_API_URL}?score_id={score_id}", json=metadata)
            elif check_response.status_code == 404:
                response = await client.post(METADATA_API_URL, json=metadata)
            else:
                raise HTTPException(status_code=500, detail="Error checking metadata existence")

            response.raise_for_status()
            print(f"MetadataAPI response: {response.json()}")  # Debug ispis
            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"HTTP error while updating metadata: {e}")  # Debug ispis
        raise HTTPException(status_code=e.response.status_code, detail="Metadata operation failed")
    except httpx.RequestError as e:
        print(f"MetadataAPI unavailable: {e}")  # Debug ispis
        raise HTTPException(status_code=503, detail="MetadataAPI service unavailable")


async def delete_metadata(score_id: str):
    """
    Delete score metadata via MetadataAPI.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{METADATA_API_URL}?score_id={score_id}")
            if response.status_code == 404:
                return {"detail": "Metadata not found or already deleted"}
            response.raise_for_status()
            return {"detail": "Metadata deleted successfully"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Metadata deletion failed"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="MetadataAPI service unavailable"
        )