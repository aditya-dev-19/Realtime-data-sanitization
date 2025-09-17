# In backend/api/routers/users.py
from fastapi import APIRouter, HTTPException, status
from .. import schemas, auth
from ..firebase_admin import db # 👈 Import the Firestore client

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    # Check if user already exists
    user_ref = db.collection('users').document(user.email)
    if user_ref.get().exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = auth.get_password_hash(user.password)

    # Create user data
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    # Save user to Firestore
    user_ref.set(user_data)
    
    return {"email": user.email}


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(user_credentials: schemas.TokenRequest):
    # Get user from Firestore
    user_ref = db.collection('users').document(user_credentials.email)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user_data = user_doc.to_dict()

    # Verify password
    if not auth.verify_password(user_credentials.password, user_data['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = auth.create_access_token(data={"sub": user_credentials.email})
    return {"access_token": access_token, "token_type": "bearer"}