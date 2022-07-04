import secrets
from typing import Union
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import logging

from uvicorn.workers import UvicornWorker

import config
from auth.managers import SignupManager, LoginManager
from sql import models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


# Class used to route Uvicorn logs onto Gunicorn
class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": "./logging.yml",
    }


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Make sure the connection is always closed after any request
        db.close()


# Not using async because SQLAlchemy has not integrated support for using await directly.
# Should use encode/databases to connect to DBs using async and await.
@app.post("/signup/", response_model=Union[schemas.User, schemas.Response])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create DB session before each request in the dependency with yield, close it afterwards.

    Return a schemas.User model, which filters out the password param from input schemas.UserCreate.

    :param user:

    :param db:

    :return:
    """
    logger.debug(f"received data: {user}")

    mgr = SignupManager()
    user_session = mgr.signup(db=db, user=user)

    # If 2FA is not enabled, return status OK
    if not user.two_factor_enabled:
        return {"status": "OK"}

    return user_session


@app.post("/login/", response_model=Union[schemas.UserSession, schemas.ResponseToken])
def login(request: Request, user: schemas.UserLogin, db: Session = Depends(get_db)):
    """

    :param request:
    :param db:
    :param user:
    :return:
    """
    logger.debug(f"received data: {user}")

    mgr = LoginManager()
    user_session = mgr.login(db=db, user=user)

    # If 2FA is not enabled, set secure cookie and return access_token
    if not user_session.two_factor_enabled:
        request.session["access_token"] = secrets.token_hex(16)
        return {"status": "OK", "access_token": request.session["access_token"]}

    logger.debug(f"Current OTP: {user_session.otp_code}")

    return user_session


@app.post("/two_factor_auth/", response_model=schemas.ResponseToken)
def two_factor_auth(request: Request, body: schemas.VerifyOTPIn, db: Session = Depends(get_db)):
    """
    Verify OTP for a previous login attempt.

    :param request:
    :param body:
    :param db:
    :return:
    """

    logger.debug(f"received data: {body}")

    mgr = LoginManager()
    mgr.verify_otp(db, body.identifier, body.otp_code)
    request.session["access_token"] = secrets.token_hex(16)
    return {"status": "OK", "access_token": request.session["access_token"]}
