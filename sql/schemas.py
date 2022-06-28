# Pydantic models
import datetime

from pydantic import BaseModel


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


class VerifyOTPIn(BaseModel):
    identifier: str
    code: str


class VerifyOTPOut(BaseModel):
    status: str
