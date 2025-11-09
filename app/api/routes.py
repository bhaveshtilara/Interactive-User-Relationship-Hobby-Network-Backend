import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.models.friendship import Friendship
from app.schemas.user import UserCreate, UserUpdate, UserOut, Message
from typing import List

# Create our API router
router = APIRouter(
    prefix="/api",
    tags=["Users"] # Groups endpoints in the /docs
)

# --- 1. Create New User ---
@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    """
    # Check if username already exists
    existing_user = await db.execute(
        select(User).where(User.username == user_in.username)
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Create new user object
    new_user = User(
        username=user_in.username,
        age=user_in.age,
        hobbies=user_in.hobbies
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database error: Username may already exist"
        )

    # We return a UserOut schema. Pydantic will handle the conversion.
    # popularity_score will be the default 0.0 for now.
    return new_user


# --- 2. Fetch All Users ---
@router.get("/users", response_model=List[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Fetch all users.
    """
    result = await db.execute(select(User).order_by(User.created_at))
    users = result.scalars().all()
    
    # We will need to update this later to calculate the
    # real popularity_score for each user.
    # For now, Pydantic defaults it to 0.0.
    return users


# --- 3. Fetch Single User ---
@router.get("/users/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetch a single user by their ID.
    """
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Later, we will calculate the score here
    # user_with_score = ...
    
    return user


# --- 4. Update User ---
@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID, 
    user_in: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's details.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get the update data, excluding unset fields
    update_data = user_in.model_dump(exclude_unset=True)

    # Check for username conflict if username is being changed
    if "username" in update_data and update_data["username"] != user.username:
        existing = await db.execute(
            select(User).where(User.username == update_data["username"])
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

    # Update the user object
    for key, value in update_data.items():
        setattr(user, key, value)
        
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database error on update"
        )
        
    return user


# --- 5. Delete User ---
@router.delete("/users/{user_id}", response_model=Message)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a user.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # --- DELETION RULE CHECK ---
    # Check if user is linked in any friendships
    friendship_check = await db.execute(
        select(Friendship).where(
            (Friendship.user_id_1 == user_id) | 
            (Friendship.user_id_2 == user_id)
        ).limit(1)
    )
    
    if friendship_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted, still has friends. Unlink first."
        )

    # If no friendships, proceed with deletion
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}