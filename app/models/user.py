import uuid
from sqlalchemy import String, Integer, DateTime, ARRAY, func, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from app.database import Base

class User(Base):
    __tablename__ = "user_account"  # Using "user" can be problematic in SQL

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        index=True
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    hobbies: Mapped[List[str]] = mapped_column(
        ARRAY(String), 
        nullable=False,
        server_default="{}"
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint('age > 0', name='age_must_be_positive'),
    )

    # This class defines how the object will be printed
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', age={self.age})>"