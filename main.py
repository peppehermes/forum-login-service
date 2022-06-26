from fastapi import FastAPI, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import logging

from sql import models, crud, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger("uvicorn.error")

app = FastAPI()


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
@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create DB session before each request in the dependency with yield, close it afterwards.
    Return a schemas.User model, which filters out the password param from input schemas.UserCreate.
    :param user:
    :param db:
    :return:
    """
    logger.debug(f"received data: {user}")

    db_user = crud.get_user_by_email(db, email=user.email)

    # Check if provided email is already registered
    if db_user:
        logger.debug("Error: email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    response = {"username": username, "password": password}

    # If 2FA is enabled for this user, redirect to 2FA endpoint
    # response = RedirectResponse(url='/redirected')

    return response


@app.post("/two_factor_auth/")
async def two_factor_auth(one_time_password: str = Form()):
    response = {"one_time_password": one_time_password}

    return response
