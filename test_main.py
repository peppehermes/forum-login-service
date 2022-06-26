from fastapi.testclient import TestClient

from main import app
from sql import schemas

client = TestClient(app)


def test_get_root():
    response = client.get(app.url_path_for("root"))
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


def test_post_signup_2fa_disabled():
    user = schemas.UserCreate(email="walterwhite@gmail.com", password="SayMyName", two_factor_enabled=False)
    # Expecting Form inputs, using data parameter
    response = client.post(app.url_path_for("signup"),
                           # data={"username": "WalterWhite", "password": "SayMyName", "two_factor_enabled": "false"})
                           data=user)

    assert response.status_code == 200
    assert response.json() == user


def test_post_signup_2fa_enabled():
    # Expecting Form inputs, using data parameter
    response = client.post(app.url_path_for("signup"),
                           data={"username": "WalterWhite", "password": "SayMyName", "two_factor_enabled": "true"})

    assert response.status_code == 200
    assert response.json() == {"username": "WalterWhite", "password": "SayMyName", "two_factor_enabled": True}
