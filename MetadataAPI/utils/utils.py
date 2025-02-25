import httpx
from fastapi import HTTPException, Header
from jose import jwt, JWTError
import httpx
from fastapi import HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from jose.exceptions import JWTError


SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"


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
