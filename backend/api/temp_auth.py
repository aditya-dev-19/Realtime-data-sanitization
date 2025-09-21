# Temporary in-memory authentication for testing
# This replaces Firebase authentication temporarily

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user storage (for testing only!)
# Pre-generate bcrypt hashes to avoid version issues
def _init_users():
    try:
        admin_hash = pwd_context.hash("admin123")
        return {
            "admin@cybersec.com": {
                "email": "admin@cybersec.com",
                "hashed_password": admin_hash
            },
            "test@example.com": {
                "email": "test@example.com", 
                "hashed_password": admin_hash
            }
        }
    except Exception as e:
        print(f"Warning: bcrypt not available, using plaintext (INSECURE!): {e}")
        # Fallback to plaintext for testing (INSECURE!)
        return {
            "admin@cybersec.com": {
                "email": "admin@cybersec.com",
                "hashed_password": "PLAIN:admin123"  # Mark as plaintext
            },
            "test@example.com": {
                "email": "test@example.com", 
                "hashed_password": "PLAIN:admin123"
            }
        }

users_db = _init_users()

def verify_password(plain_password, hashed_password):
    try:
        # Check if this is a plaintext fallback
        if hashed_password.startswith("PLAIN:"):
            return plain_password == hashed_password[6:]  # Remove "PLAIN:" prefix
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Warning: bcrypt hashing failed, using plaintext (INSECURE!): {e}")
        return f"PLAIN:{password}"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str):
    user = users_db.get(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_user(email: str, password: str):
    if email in users_db:
        return None  # User already exists
    
    hashed_password = get_password_hash(password)
    users_db[email] = {
        "email": email,
        "hashed_password": hashed_password
    }
    return {"email": email}