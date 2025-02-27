from fastapi import HTTPException
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from jose.exceptions import JWTError

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/users/login")


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
