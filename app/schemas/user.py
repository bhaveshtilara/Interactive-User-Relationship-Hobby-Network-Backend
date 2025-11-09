import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

# --- Base Schema ---
# Contains common fields used for both creation and updates.
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., gt=0) # 'gt=0' means "greater than 0"
    hobbies: List[str] = Field(default_factory=list)


# --- Create Schema ---
# Used when creating a new user (POST /api/users)
class UserCreate(UserBase):
    pass # No extra fields needed


# --- Update Schema ---
# Used when updating an existing user (PUT /api/users/:id) - All fields are optional.
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, gt=0)
    hobbies: Optional[List[str]] = None


# --- Output Schema ---
# This is the schema that will be SENT to the user - It includes fields from the database like id and created_at.
class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    # We add popularityScore here.
    # It's not in the DB, so we'll compute it later - For now, it will just return the default of 0.0.
    popularity_score: float = 0.0

    # This 'model_config' tells Pydantic to read data
    # from SQLAlchemy model attributes (e.g., user.id)
    model_config = ConfigDict(from_attributes=True)


# --- Helper Schema ---
# A generic message for success/error responses
class Message(BaseModel):
    message: str