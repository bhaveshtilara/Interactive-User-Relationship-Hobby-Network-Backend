import uuid
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class Friendship(Base):
    __tablename__ = "friendship"

    # We reference the user table's ID column
    user_id_1: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id_2: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), 
        nullable=False
    )

    __table_args__ = (
        # Ensures (A, B) and (B, A) can't both exist, 
        # and A cannot be friends with A
        CheckConstraint("user_id_1 < user_id_2", name="ordered_friendship_ids"),
        
        # Defines the composite primary key
        PrimaryKeyConstraint("user_id_1", "user_id_2"),
    )

    def __repr__(self) -> str:
        return f"<Friendship(user1='{self.user_id_1}', user2='{self.user_id_2}')>"