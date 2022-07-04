# SQLAlchemy models
import secrets
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.event import listen
from sqlalchemy.orm import relationship

import config
from auth.otp import TOTPManager
from .database import Base
from auth.pwd.pwd_context import get_password_hash


def hash_user_password(mapper, context, target):
    """SQLAlchemy event hook for hashing raw passwords"""
    target.hash_password()


def make_identifier():
    return secrets.token_hex(16)


class User(Base):
    """Describes a user entity with basic info, 2FA flag and secret fot OTP generation"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    secret = Column(String, default=TOTPManager.generate_secret(), nullable=False)

    def hash_password(self):
        """Stores hashed password into DB instead of the raw one"""
        self.hashed_password = get_password_hash(self.hashed_password)


class LoginAttempt(Base):
    """Describes a single login attempt with an identifier"""

    __tablename__ = "login_attempt"

    id = Column(Integer(), primary_key=True)
    identifier = Column(String(), index=True, nullable=False, default=make_identifier)
    timestamp = Column(DateTime(), default=datetime.utcnow)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)

    user = relationship("User", uselist=False)

    # Possibly, add more meta info ? status, IP, etc

    def is_valid(self) -> bool:
        return (
            datetime.utcnow() - self.timestamp
        ).seconds < config.AUTH_OTP_THRESHOLD_SECONDS


# Register for new user creation event.
# Hash its password before storing it
listen(User, "before_insert", hash_user_password)
