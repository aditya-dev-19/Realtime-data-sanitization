from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, auth
from ..firebase_admin import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=dict)
async def create_user(user: schemas.UserCreate):
    """Register a new user"""
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Check if user already exists
        user_ref = db.collection('users').document(user.email)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            logger.warning(f"Registration failed - email already exists: {user.email}")
            raise HTTPException(
                status_code=400, 
                detail="Email already registered"
            )

        # Hash the password
        hashed_password = auth.get_password_hash(user.password)

        # Create user data
        user_data = {
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": auth.datetime.utcnow(),
            "disabled": False
        }
        
        # Save user to Firestore
        user_ref.set(user_data)
        logger.info(f"User registered successfully: {user.email}")
        
        return {"message": "User created successfully", "email": user.email}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during registration"
        )

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(user_credentials: schemas.TokenRequest):
    """Login and get access token"""
    try:
        logger.info(f"Login attempt for email: {user_credentials.email}")
        
        # Get user from Firestore
        user_ref = db.collection('users').document(user_credentials.email)
        user_doc = user_ref.get()

        if not user_doc.exists:
            logger.warning(f"Login failed - user not found: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = user_doc.to_dict()

        # Check if user is disabled
        if user_data.get('disabled', False):
            logger.warning(f"Login failed - user disabled: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not auth.verify_password(user_credentials.password, user_data['hashed_password']):
            logger.warning(f"Login failed - incorrect password: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth.create_access_token(
            data={"sub": user_credentials.email}
        )
        
        logger.info(f"Login successful for: {user_credentials.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {user_credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during login"
        )

# Health check endpoint
@router.get("/auth/health")
async def auth_health_check():
    """Check if authentication service is working"""
    try:
        # Test Firestore connection
        test_ref = db.collection('users').limit(1)
        list(test_ref.stream())  # This will throw if connection fails
        return {"status": "healthy", "firestore": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}