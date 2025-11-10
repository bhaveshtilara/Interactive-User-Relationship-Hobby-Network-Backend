import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

# --- Base Schema ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., gt=0) # 'gt=0' means "greater than 0"
    hobbies: List[str] = Field(default_factory=list)

# --- Create Schema ---
class UserCreate(UserBase):
    pass

# --- Update Schema ---
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, gt=0)
    hobbies: Optional[List[str]] = None

# --- Output Schema (MODIFIED) ---
# This is the schema that will be SENT to the user.
class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    # This field will be populated by our endpoints
    popularity_score: float = Field(default=0.0)

    model_config = ConfigDict(from_attributes=True)

# --- Helper Schema ---
class Message(BaseModel):
    message: str

# --- NEW SCHEMA for Linking ---
class FriendRequest(BaseModel):
    friend_id: uuid.UUID