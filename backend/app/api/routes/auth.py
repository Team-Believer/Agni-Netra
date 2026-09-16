from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.api.dependencies import get_current_user

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    username: str

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, query database here. We use dev credentials.
    if form_data.username != settings.AUTH_DEV_USERNAME or form_data.password != settings.AUTH_DEV_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=form_data.username, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"username": form_data.username}
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

@router.post("/logout")
def logout():
    # Frontend handles token deletion.
    return {"message": "Successfully logged out"}
