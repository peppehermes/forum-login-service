import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

for k, v in os.environ.items():
    if k == "DATABASE_TEST_URL":
        SQLALCHEMY_DATABASE_URL = v
