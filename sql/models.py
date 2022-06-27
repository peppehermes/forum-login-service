# SQLAlchemy models
from sqlalchemy import Column, Boolean, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    two_factor_enabled = Column(Boolean, default=False)
    secret = Column(String)
