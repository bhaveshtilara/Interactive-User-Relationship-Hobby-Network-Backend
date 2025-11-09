# This file makes Python treat the 'models' directory as a package.
# It also conveniently exports our Base and models.

from app.database import Base
from .user import User
from .friendship import Friendship