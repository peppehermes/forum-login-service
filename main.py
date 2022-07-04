import secrets
from typing import Union
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import logging.config
import yaml

import config
from auth.managers import SignupManager, LoginManager
from sql import models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


with open(config.LOG_CONFIG) as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(log_config)

app = FastAPI()

# Add SessionMiddleware to store the access_token
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


# Dependency
# Create DB session before each request in the dependency with yield, close it afterwards.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Make sure the connection is always closed after any request
        db.close()


# Not using async because SQLAlchemy has not integrated support for using await directly.
# Should use encode/databases to connect to DBs using async and await.
@app.post("/auth/signup/", response_model=Union[schemas.User, schemas.Response])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new User, provided its email, password and 2FA preference.

    Return a User model, which filters out the password param from input user.


    Request body: JSON object with following params:

        - email: string, the user email address

        - password: string, the user password
        (should be sent hashed by the client, but for simplicity it is sent as plain text)

        - two_factor_enabled: boolean, states if the user wants to enable or not 2FA


    Responses:

    JSON object with following params, if 2FA is enabled:

        - email: string, the user email address

        - two_factor_enabled: boolean, states if the user wants to enable or not 2FA

        - id: int, the user identifier

    If 2FA is not enabled, {"status": "OK"} is returned.
    """
    logging.debug(f"received data: {user}")

    mgr = SignupManager()
    user_session = mgr.signup(db=db, user=user)

    # If 2FA is not enabled, return status OK
    if not user.two_factor_enabled:
        return {"status": "OK"}

    return user_session


@app.post(
    "/auth/login/", response_model=Union[schemas.UserSession, schemas.ResponseToken]
)
def login(request: Request, user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint for user login. Receive user email and password.

    Return a UserSession or a ResponseToken, depending on if the user has 2FA enabled or not.


    Request body: JSON object with following params:

        - email: string, the user email address

        - password: string, the user password


    Responses:

    JSON object with following params, if 2FA is enabled:

        - email: string, the user email address

        - two_factor_enabled: boolean, states if the user wants to enable or not 2FA

        - id: int, the user identifier

        - login_identifier: string, code used as identifier for login attempt, to be used in /two_factor_auth endpoint

        - otp_code: string, time-based OTP code, to be used in /two_factor_auth endpoint

    If 2FA is not enabled, a JSON object with following params is returned:

        - status: string, should be "OK" if all goes well.

        - access_token: string, token to be used for subsequent calls; it certifies that the used is logged.
    """
    logging.debug(f"received data: {user}")

    mgr = LoginManager()
    user_session = mgr.login(db=db, user=user)

    # If 2FA is not enabled, set secure cookie and return access_token
    if not user_session.two_factor_enabled:
        request.session["access_token"] = secrets.token_hex(16)
        return {"status": "OK", "access_token": request.session["access_token"]}

    logging.debug(f"Current OTP: {user_session.otp_code}")

    return user_session


@app.post("/auth/two_factor/", response_model=schemas.ResponseToken)
def two_factor_auth(
    request: Request, body: schemas.VerifyOTPIn, db: Session = Depends(get_db)
):
    """
    Verify OTP for a previous login attempt.


    Request body: JSON object with following params:

        - identifier: string, code used as identifier for login attempt, received by /login endpoint

        - password: string, time-based OTP code, received by /login endpoint


    Response: JSON object with following params:

        - status: string, should be "OK" if all goes well.

        - access_token: string, token to be used for subsequent calls; it certifies that the used is logged.
    """

    logging.debug(f"received data: {body}")

    mgr = LoginManager()
    mgr.verify_otp(db, body.identifier, body.otp_code)
    request.session["access_token"] = secrets.token_hex(16)

    return {"status": "OK", "access_token": request.session["access_token"]}
