from typing import Generator
from sqlalchemy.orm import Session
from backend.app.database.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError

from backend.app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

class TokenPayload(BaseModel):
    sub: str = None

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        return settings.AUTH_DEV_USERNAME
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        return settings.AUTH_DEV_USERNAME
        
    user = token_data.sub
    if not user:
        return settings.AUTH_DEV_USERNAME
        
    return user
