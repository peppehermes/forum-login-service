from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, secret=None):
    # TODO make the password passing more secure
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email,
                          hashed_password=fake_hashed_password,
                          two_factor_enabled=user.two_factor_enabled,
                          secret=secret,
                          )
    db.add(db_user)
    db.commit()

    # Refresh local instance of db_user, so that it contains any new data from the DB
    # e.g. the generated ID
    db.refresh(db_user)
    return db_user
