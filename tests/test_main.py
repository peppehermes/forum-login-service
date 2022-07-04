import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from sql.database import Base, custom_create_engine
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = custom_create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency override, using TestingSession
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


def test_signup_2fa_disabled(test_db):
    response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": False,
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "status" in data
    assert data["status"] == "OK"


def test_signup_2fa_enabled(test_db):
    response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": True,
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True


def test_signup_already_registered(test_db):
    client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": True,
        },
    )

    # Repeat post request with same data
    response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": True,
        },
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Email already registered"


def test_login_two_factor_disabled_correct_password(test_db):
    signup_response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": False,
        },
    )

    assert signup_response.status_code == 200, signup_response.text
    data = signup_response.json()
    assert "status" in data
    assert data["status"] == "OK"

    login_response = client.post(
        app.url_path_for("login"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
        },
    )

    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    assert "status" in data
    assert data["status"] == "OK"

    assert "access_token" in data


def test_login_two_factor_disabled_wrong_password(test_db):
    signup_response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": False,
        },
    )

    assert signup_response.status_code == 200, signup_response.text
    data = signup_response.json()
    assert "status" in data
    assert data["status"] == "OK"

    login_response = client.post(
        app.url_path_for("login"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "test",
        },
    )

    assert login_response.status_code == 401, login_response.text
    data = login_response.json()
    assert "detail" in data
    assert data["detail"] == "No user can be found matching provided credentials"

    assert "access_token" not in data


def test_login_two_factor_enabled_wrong_otp(test_db):
    signup_response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": True,
        },
    )

    assert signup_response.status_code == 200, signup_response.text
    data = signup_response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True

    login_response = client.post(
        app.url_path_for("login"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
        },
    )

    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True
    assert "login_identifier" in data
    assert "otp_code" in data
    assert data["otp_code"] is not None

    two_factor_response = client.post(
        app.url_path_for("two_factor_auth"),
        json={"identifier": data["login_identifier"], "otp_code": "123456"},
    )

    assert two_factor_response.status_code == 401, two_factor_response.text
    data = two_factor_response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid OTP received"

    assert "access_token" not in data


def test_login_two_factor_enabled_correct_otp(test_db):
    signup_response = client.post(
        app.url_path_for("signup"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
            "two_factor_enabled": True,
        },
    )

    assert signup_response.status_code == 200, signup_response.text
    data = signup_response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True

    signup_user_id = data["id"]

    login_response = client.post(
        app.url_path_for("login"),
        json={
            "email": "walterwhite@gmail.com",
            "password": "SayMyName",
        },
    )

    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    assert data["email"] == "walterwhite@gmail.com"
    assert "id" in data
    assert data["two_factor_enabled"] is True
    assert "login_identifier" in data
    assert "otp_code" in data
    assert data["otp_code"] is not None

    login_identifier = data["login_identifier"]
    login_otp_code = data["otp_code"]
    login_user_id = data["id"]

    assert login_user_id == signup_user_id

    two_factor_response = client.post(
        app.url_path_for("two_factor_auth"),
        json={"identifier": login_identifier, "otp_code": login_otp_code},
    )

    assert two_factor_response.status_code == 200, two_factor_response.text
    data = two_factor_response.json()
    assert "status" in data
    assert data["status"] == "OK"

    assert "access_token" in data
