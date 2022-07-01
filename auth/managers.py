from typing import Optional

from fastapi import HTTPException
import pyotp

import config
from auth.exceptions import InvalidUserCredentials, AlreadyRegisteredUser
from auth.otp import TOTPManager
from auth.pwd.pwd_context import verify_password
from sql import crud
from sql.models import User, LoginAttempt
from sql.schemas import UserCreate, UserSession


class LoginManager:
    """ Manager for the login process. Utilizes two-step TOTP checking """

    @staticmethod
    def authenticate(session, user: UserCreate) -> Optional[User]:
        """ Fetches the user from DB and validates password """
        db_user = crud.get_user_by_email(session, email=user.email)
        if not db_user or not verify_password(user.email, user.password):
            return None
        return db_user

    def login(self, session, user: UserCreate) -> LoginAttempt:
        """ Tries to log the user in """

        db_user = self.authenticate(session, user)
        if not db_user:
            # raise InvalidUserCredentials
            raise HTTPException(status_code=401, detail="No user can be found matching provided credentials")

        attempt = LoginAttempt(user=db_user)
        session.add(attempt)
        session.commit()
        return attempt

    @staticmethod
    def verify_otp(db, identifier, otp_code):
        """ Verifies OTP for a single login attempt """
        attempt = db.query(LoginAttempt).filter_by(identifier=identifier).first()
        conditions = [
            attempt,
            attempt.is_valid(),
            TOTPManager.validate_otp(attempt.user.secret, otp_code),
        ]
        if not all(conditions):
            # raise InvalidOTP
            raise HTTPException(status_code=401, detail="Invalid OTP received")
        return True


class SignupManager:
    """ Manager for the signup process. Utilizes two-step TOTP checking """

    @staticmethod
    def check_email(session, user: UserCreate):
        """ Check that the provided email has not been already used """
        db_user = crud.get_user_by_email(session, email=user.email)

        # Check if provided email is already registered
        if db_user:
            # raise AlreadyRegisteredUser
            raise HTTPException(status_code=400, detail="Email already registered")

    def signup(self, session, user: UserCreate) -> UserSession:
        """ Tries to register the user """

        self.check_email(session, user)

        db_user = crud.create_user(db=session, user=user)
        login_attempt = crud.create_login_attempt(db=session, db_user=db_user)
        otp_code = None
        if db_user.two_factor_enabled:
            otp_code = TOTPManager.generate_otp(db_user.secret)

        user_session = UserSession(
            email=db_user.email,
            id=db_user.id,
            two_factor_enabled=db_user.two_factor_enabled,
            login_identifier=login_attempt.identifier,
            otp_code=otp_code
        )

        return user_session
