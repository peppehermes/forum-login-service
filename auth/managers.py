from typing import Optional

from fastapi import HTTPException

from auth.exceptions import InvalidUserCredentials, AlreadyRegisteredUser
from auth.otp import TOTPManager
from auth.pwd.pwd_context import verify_password
from sql import crud
from sql.models import User, LoginAttempt
from sql.schemas import UserCreate, UserSession, UserLogin
from sqlalchemy.orm import Session


class LoginAttemptManager:
    """ Manager for the login attempt. Used to save a new login attempt and activate a new user session """

    @staticmethod
    def generate_user_session(db: Session, db_user: User):
        login_attempt = crud.create_login_attempt(db=db, db_user=db_user)

        otp_code = None
        if db_user.two_factor_enabled:
            otp_code = TOTPManager(user_secret=db_user.secret).generate_otp()

        user_session = UserSession(
            email=db_user.email,
            id=db_user.id,
            two_factor_enabled=db_user.two_factor_enabled,
            login_identifier=login_attempt.identifier,
            otp_code=otp_code
        )

        return user_session


class LoginManager:
    """ Manager for the login process. Utilizes two-step TOTP checking """

    @staticmethod
    def authenticate(db: Session, user: UserLogin) -> Optional[User]:
        """ Fetches the user from DB and validates password """
        db_user = crud.get_user_by_email(db, email=user.email)
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            return None
        return db_user

    def login(self, db: Session, user: UserLogin) -> UserSession:
        """ Tries to log the user in """

        db_user = self.authenticate(db, user)
        if not db_user:
            # raise InvalidUserCredentials
            raise HTTPException(status_code=401, detail="No user can be found matching provided credentials")

        return LoginAttemptManager.generate_user_session(db=db, db_user=db_user)

    @staticmethod
    def verify_otp(db: Session, identifier, otp_code):
        """ Verifies OTP for a single login attempt """
        attempt = db.query(LoginAttempt).filter_by(identifier=identifier).first()
        conditions = [
            attempt,
            attempt.is_valid(),
            TOTPManager(user_secret=attempt.user.secret).validate_otp(otp_code),
        ]
        if not all(conditions):
            # raise InvalidOTP
            raise HTTPException(status_code=401, detail="Invalid OTP received")
        return True


class SignupManager:
    """ Manager for the signup process. Utilizes two-step TOTP checking """

    @staticmethod
    def check_email(db: Session, user: UserCreate):
        """ Check that the provided email has not been already used """
        db_user = crud.get_user_by_email(db, email=user.email)

        # Check if provided email is already registered
        if db_user:
            # raise AlreadyRegisteredUser
            raise HTTPException(status_code=400, detail="Email already registered")

    def signup(self, db: Session, user: UserCreate) -> UserSession:
        """ Tries to register the user """

        self.check_email(db, user)

        db_user = crud.create_user(db=db, user=user)

        return LoginAttemptManager.generate_user_session(db=db, db_user=db_user)
