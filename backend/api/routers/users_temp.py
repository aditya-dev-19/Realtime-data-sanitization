# Temporary users router for testing authentication
# This replaces the Firebase-dependent users.py temporarily

from fastapi import APIRouter, HTTPException, status
from .. import schemas
from ..temp_auth import authenticate_user, create_user, create_access_token

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def create_user_temp(user: schemas.UserCreate):
    # Try to create user
    result = create_user(user.email, user.password)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return result

@router.post("/token", response_model=schemas.Token)
def login_for_access_token_temp(user_credentials: schemas.TokenRequest):
    # Authenticate user
    user = authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_credentials.email})
    return {"access_token": access_token, "token_type": "bearer"}