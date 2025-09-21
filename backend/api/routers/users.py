from fastapi import APIRouter, HTTPException, status
from datetime import datetime  # 👈 ADD THIS IMPORT
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
        
        # Validate email format
        if not user.email or '@' not in user.email:
            raise HTTPException(
                status_code=400, 
                detail="Invalid email format"
            )
        
        # Validate password
        if not user.password or len(user.password) < 6:
            raise HTTPException(
                status_code=400, 
                detail="Password must be at least 6 characters long"
            )
        
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
        logger.info(f"Password hashed successfully for: {user.email}")

        # Create user data with proper timestamp
        user_data = {
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),  # 👈 FIXED: proper datetime
            "disabled": False
        }
        
        # Save user to Firestore
        user_ref.set(user_data)
        logger.info(f"User data saved to Firestore for: {user.email}")
        
        # Verify the user was actually saved
        saved_doc = user_ref.get()
        if not saved_doc.exists:
            logger.error(f"Failed to verify user creation for: {user.email}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create user account"
            )
        
        logger.info(f"User registered successfully and verified: {user.email}")
        return {"message": "User created successfully", "email": user.email}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user.email}: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during registration: {str(e)}"
        )

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(user_credentials: schemas.TokenRequest):
    """Login and get access token"""
    try:
        logger.info(f"Login attempt for email: {user_credentials.email}")
        
        # Validate input
        if not user_credentials.email or not user_credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
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
        logger.info(f"User data retrieved for: {user_credentials.email}")

        # Check if user is disabled
        if user_data.get('disabled', False):
            logger.warning(f"Login failed - user disabled: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        stored_hash = user_data.get('hashed_password')
        if not stored_hash:
            logger.error(f"No hashed password found for user: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account configuration error"
            )
        
        if not auth.verify_password(user_credentials.password, stored_hash):
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
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during login: {str(e)}"
        )

@router.get("/auth/health")
async def auth_health_check():
    """Check if authentication service is working"""
    try:
        # Test Firestore connection with a simple read
        test_ref = db.collection('users').limit(1)
        docs = list(test_ref.stream())
        
        # Test write capability
        health_ref = db.collection('_health').document('auth_check')
        health_ref.set({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'test': True
        })
        
        # Clean up
        health_ref.delete()
        
        return {
            "status": "healthy", 
            "firestore": "connected",
            "read_access": "ok",
            "write_access": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/auth/debug")
async def debug_users():
    """Debug endpoint to check users (REMOVE IN PRODUCTION)"""
    try:
        users_ref = db.collection('users').limit(5)
        users = []
        for doc in users_ref.stream():
            user_data = doc.to_dict()
            # Don't include password hash in response
            safe_data = {
                'email': doc.id,
                'created_at': user_data.get('created_at'),
                'disabled': user_data.get('disabled', False),
                'has_password': 'hashed_password' in user_data
            }
            users.append(safe_data)
        
        return {
            "total_users": len(users),
            "users": users,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}