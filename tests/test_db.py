# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy.orm import sessionmaker
#
# from sql.database import Base, custom_create_engine
# from sql import crud
# from main import app, get_db
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
#
# engine = custom_create_engine(SQLALCHEMY_DATABASE_URL)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# # Dependency override, using TestingSession
# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
#
# app.dependency_overrides[get_db] = override_get_db
#
#
# # Use pytest fixture to create tables and drop them between each test
# @pytest.fixture()
# def test_db():
#     Base.metadata.create_all(bind=engine)
#     yield
#     Base.metadata.drop_all(bind=engine)
#
#
# client = TestClient(app)
#
#
# def test_create_user(test_db):
#     response = client.post(
#         app.url_path_for("signup"),
#         json={"email": "walterwhite@gmail.com", "password": "SayMyName",
#               "two_factor_enabled": False},
#     )
#
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "id" in data
#
#     user_id = data["id"]
#     user = crud.get_user(, user_id)
#
#     assert user["email"] == "walterwhite@gmail.com"
#     assert user["two_factor_enabled"] is False
#     assert "secret" in user
#     assert user["secret"] is None
#
#
# def test_create_user_secret(test_db):
#     response = client.post(
#         app.url_path_for("signup"),
#         json={"email": "walterwhite@gmail.com", "password": "SayMyName",
#               "two_factor_enabled": True},
#     )
#
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "id" in data
#
#     user_id = data["id"]
#     user = crud.get_user(test_db, user_id)
#
#     assert user["email"] == "walterwhite@gmail.com"
#     assert user["two_factor_enabled"] is True
#     assert "secret" in user
#     assert user["secret"] is not None
