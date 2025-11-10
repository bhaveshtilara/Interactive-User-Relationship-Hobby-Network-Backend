import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from app.database import get_db
from app.models.user import User
from app.models.friendship import Friendship
# --- NEW/MODIFIED IMPORTS ---
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserOut, 
    Message, 
    FriendRequest
)
from app.services.user_service import calculate_popularity_score
# --- END NEW/MODIFIED IMPORTS ---
from typing import List

router = APIRouter(
    prefix="/api",
    tags=["Users", "Graph"] # Add "Graph" tag
)

# --- 1. Create New User (MODIFIED) ---
# No change to logic, but the UserOut response will now show 0.0
@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(
        select(User).where(User.username == user_in.username)
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
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
    
    # We can just return the user. The score will be the default (0.0),
    # which is correct for a new user with no friends.
    return new_user


# --- 2. Fetch All Users (MODIFIED) ---
@router.get("/users", response_model=List[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at))
    users = result.scalars().all()
    
    # We must calculate the score for each user
    users_with_scores = []
    for user in users:
        score = await calculate_popularity_score(user, db)
        # Manually create the UserOut Pydantic model
        user_out = UserOut.model_validate(user)
        user_out.popularity_score = score
        users_with_scores.append(user_out)
        
    return users_with_scores


# --- 3. Fetch Single User (MODIFIED) ---
@router.get("/users/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Calculate the score for this user
    score = await calculate_popularity_score(user, db)
    user_out = UserOut.model_validate(user)
    user_out.popularity_score = score
    
    return user_out


# --- 4. Update User (MODIFIED) ---
@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID, 
    user_in: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] != user.username:
        existing = await db.execute(
            select(User).where(User.username == update_data["username"])
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

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
    
    # Calculate score for the updated user
    score = await calculate_popularity_score(user, db)
    user_out = UserOut.model_validate(user)
    user_out.popularity_score = score
        
    return user_out


# --- 5. Delete User ---
# (No changes needed, the logic is still correct)
@router.delete("/users/{user_id}", response_model=Message)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
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

    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}


# --- 6. NEW: Create Relationship (Link) ---
@router.post("/users/{user_id}/link", response_model=Message, tags=["Users"])
async def create_friendship(
    user_id: uuid.UUID, 
    request: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a friendship link between two users.
    """
    friend_id = request.friend_id

    # Rule: Cannot link to oneself
    if user_id == friend_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create friendship with oneself"
        )

    # Check if both users exist
    user_1 = await db.get(User, user_id)
    user_2 = await db.get(User, friend_id)
    
    if not user_1 or not user_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both users not found"
        )

    # Enforce our "user_id_1 < user_id_2" constraint
    if user_id < friend_id:
        id_1, id_2 = user_id, friend_id
    else:
        id_1, id_2 = friend_id, user_id
        
    # Create the new friendship link
    new_friendship = Friendship(user_id_1=id_1, user_id_2=id_2)
    
    try:
        db.add(new_friendship)
        await db.commit()
    except IntegrityError:
        # This catches the PrimaryKeyViolation (friendship already exists)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Friendship already exists"
        )

    return {"message": "Friendship created successfully"}


# --- 7. NEW: Remove Relationship (Unlink) ---
@router.delete("/users/{user_id}/unlink", response_model=Message, tags=["Users"])
async def remove_friendship(
    user_id: uuid.UUID, 
    request: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a friendship link between two users.
    """
    friend_id = request.friend_id

    # Enforce "user_id_1 < user_id_2" to find the correct row
    if user_id < friend_id:
        id_1, id_2 = user_id, friend_id
    else:
        id_1, id_2 = friend_id, user_id
        
    # Find the friendship
    friendship_query = await db.execute(
        select(Friendship).where(
            (Friendship.user_id_1 == id_1) & 
            (Friendship.user_id_2 == id_2)
        )
    )
    friendship = friendship_query.scalars().first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
        
    # Delete the friendship
    await db.delete(friendship)
    await db.commit()
    
    return {"message": "Friendship removed successfully"}


# --- 8. NEW: Get Graph Data ---
@router.get("/graph", response_model=dict, tags=["Graph"])
async def get_graph_data(db: AsyncSession = Depends(get_db)):
    """
    Fetch all data needed to render the React Flow graph.
    Returns lists of nodes and edges.
    """
    
    # 1. Fetch all users
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()
    
    # 2. Fetch all friendships (edges)
    edges_result = await db.execute(select(Friendship))
    friendships = edges_result.scalars().all()

    nodes = []
    # 3. Process users into nodes and calculate scores
    for user in users:
        score = await calculate_popularity_score(user, db)
        
        # Determine node type based on score
        if score > 10:
            node_type = "VeryHighScoreNode"
        elif score > 5:
            node_type = "HighScoreNode"
        else:
            node_type = "LowScoreNode"
        
        nodes.append({
            "id": str(user.id),
            "type": node_type,
            "position": {"x": 0, "y": 0}, # Frontend will handle layout
            "data": {
                "label": user.username, # 'label' is used by React Flow
                "age": user.age,
                "hobbies": user.hobbies,
                "popularityScore": score,
                "createdAt": user.created_at.isoformat()
            }
        })
        
    # 4. Process friendships into edges
    edges = [
        {
            "id": f"e-{fs.user_id_1}-{fs.user_id_2}",
            "source": str(fs.user_id_1),
            "target": str(fs.user_id_2)
        }
        for fs in friendships
    ]
    
    return {"nodes": nodes, "edges": edges}