from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


def test_post_signup_2fa_disabled():
    # Expecting Form inputs, using data parameter
    response = client.post("/signup/",
                           data={"username": "WalterWhite", "password": "SayMyName", "two_factor_enabled": "false"})

    assert response.status_code == 200
    assert response.json() == {"username": "WalterWhite", "password": "SayMyName", "two_factor_enabled": "false"}
