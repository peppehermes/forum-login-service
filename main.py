import secrets
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi import FastAPI, Form, Depends
from sqlalchemy.orm import Session
import logging

import config
from auth.managers import SignupManager, LoginManager
from sql import models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Make sure the connection is always closed after any request
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World!"}


# Not using async because SQLAlchemy has not integrated support for using await directly.
# Should use encode/databases to connect to DBs using async and await.
@app.post("/signup/", response_model=schemas.UserSession)
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
    return mgr.signup(session=db, user=user)


@app.post("/login/")
def login(username: str = Form(), password: str = Form()):
    """

    :param username:
    :param password:
    :return:
    """
    response = {"username": username, "password": password}

    return response


@app.post("/two_factor_auth/", response_model=schemas.VerifyOTPOut)
def two_factor_auth(request: Request, body: schemas.VerifyOTPIn, db: Session = Depends(get_db)):
    """

    :param request:
    :param body:
    :param db:
    :return:
    """

    """ Verify OTP for a previous login attempt """
    logger.debug(f"received data: {body}")

    mgr = LoginManager()
    mgr.verify_otp(db, body.identifier, body.otp_code)
    request.session["access_token"] = secrets.token_hex(16)
    return {"status": "OK"}
