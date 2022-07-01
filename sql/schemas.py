# Pydantic models
from typing import Optional

from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    email: str
    two_factor_enabled: bool


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    # Get object params from attribute e.g. data.id
    class Config:
        orm_mode = True


class UserSession(User):
    login_identifier: str
    otp_code: Optional[str]


class VerifyOTPIn(BaseModel):
    identifier: str
    otp_code: str


class VerifyOTPOut(BaseModel):
    status: str
    access_token: Optional[str]
