from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    """Get user from DB given its ID"""

    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Get user from DB given its email"""

    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """Create new user and insert into DB"""

    db_user = models.User(
        email=user.email,
        hashed_password=user.password,
        two_factor_enabled=user.two_factor_enabled,
    )
    db.add(db_user)
    db.commit()

    # Refresh local instance of db_user, so that it contains any new data from the DB
    # e.g. the generated ID
    db.refresh(db_user)
    return db_user


def create_login_attempt(db: Session, db_user: models.User):
    """Create new login attempt and insert into DB"""

    attempt = models.LoginAttempt(user=db_user)
    db.add(attempt)
    db.commit()

    # Refresh local instance of db_user, so that it contains any new data from the DB
    # e.g. the generated ID
    db.refresh(attempt)

    return attempt
