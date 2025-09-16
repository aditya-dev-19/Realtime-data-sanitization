from pydantic import BaseModel
from typing import Optional

# --- Pydantic Models for Data Validation ---

class Token(BaseModel):
    """Defines the shape of an access token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Defines the data contained within a JWT."""
    email: Optional[str] = None

# [ADDED] This class is needed for the login endpoint
class TokenRequest(BaseModel):
    """Defines the shape of a login request body."""
    email: str
    password: str

class UserBase(BaseModel):
    """Base model for user data."""
    email: str

class UserCreate(UserBase):
    """Model for creating a new user. Expects a password."""
    password: str

class User(UserBase):
    """Model for representing a user retrieved from the database."""
    # This can be expanded with more user fields if needed.
    class Config:
        # This allows the model to be created from database objects.
        orm_mode = True