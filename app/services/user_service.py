import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.friendship import Friendship
from typing import List, Set

async def get_user_friends(
    user_id: uuid.UUID, 
    db: AsyncSession
) -> List[User]:
    """
    Fetches all User objects that are friends with the given user_id.
    """
    
    # 1. Find all friend IDs
    friend_id_query = (
        select(Friendship.user_id_1)
        .where(Friendship.user_id_2 == user_id)
        .union(
            select(Friendship.user_id_2)
            .where(Friendship.user_id_1 == user_id)
        )
    )
    
    friend_ids_result = await db.execute(friend_id_query)
    friend_ids = friend_ids_result.scalars().all()
    
    if not friend_ids:
        return []

    # 2. Fetch all User objects for those IDs
    friends_query = select(User).where(User.id.in_(friend_ids))
    friends_result = await db.execute(friends_query)
    friends = friends_result.scalars().all()
    
    return friends

async def calculate_popularity_score(
    user: User, 
    db: AsyncSession
) -> float:
    """
    Calculates the popularity score for a single user.
    Formula: score = (number of friends) + (total hobbies shared with friends * 0.5)
    """
    
    # 1. Get all friend objects
    friends = await get_user_friends(user.id, db)
    
    friend_count = len(friends)
    if friend_count == 0:
        return 0.0

    # 2. Calculate shared hobbies
    user_hobbies: Set[str] = set(user.hobbies)
    total_shared_hobbies = 0
    
    for friend in friends:
        friend_hobbies: Set[str] = set(friend.hobbies)
        shared_count = len(user_hobbies.intersection(friend_hobbies))
        total_shared_hobbies += shared_count
        
    # 3. Apply formula
    score = friend_count + (total_shared_hobbies * 0.5)
    
    return score