import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from sql.database import Base, custom_create_engine
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = custom_create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Use pytest fixture to create tables and drop them between each test
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_get_root(test_db):
    response = client.get(app.url_path_for("root"))
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


def test_post_signup_2fa_disabled(test_db):
    response = client.post(
        app.url_path_for("signup"),
        json={"email": "walterwhite@gmail.com", "password": "SayMyName",
              "two_factor_enabled": False},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is False


def test_post_signup_2fa_enabled(test_db):
    response = client.post(
        app.url_path_for("signup"),
        json={"email": "walterwhite@gmail.com", "password": "SayMyName",
              "two_factor_enabled": True},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True


def test_post_signup_already_registered(test_db):
    client.post(
        app.url_path_for("signup"),
        json={"email": "walterwhite@gmail.com", "password": "SayMyName",
              "two_factor_enabled": True},
    )

    # Repeat post request with same data
    response = client.post(
        app.url_path_for("signup"),
        json={"email": "walterwhite@gmail.com", "password": "SayMyName",
              "two_factor_enabled": True},
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Email already registered"
