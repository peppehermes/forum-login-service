""" Module containing common exception class for typical LEAN FastAPI projects """
from typing import Any

from fastapi import HTTPException


class CommonError(HTTPException):
    code: str
    message: str
    additional: Any = None
    status_code: int = 400

    def content(self):
        return {
            "code": self.code,
            "message": self.message,
            "additional_info": self.additional,
        }


class InvalidUserCredentials(CommonError):
    code = "invalid_user_credentials"
    message = "No user can be found matching provided credentials"
    status_code = 401


class AlreadyRegisteredUser(CommonError):
    code = "already_registered_user"
    message = "Email already registered"
    status_code = 401
