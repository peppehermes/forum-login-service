from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"


def custom_create_engine(url):
    return create_engine(
        url, connect_args={"check_same_thread": False}
    )


engine = custom_create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
