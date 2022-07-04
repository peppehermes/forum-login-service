import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"
APP_NAME = "Login OTP App"

AUTH_OTP_THRESHOLD_SECONDS = 300  # OTPs are valid for 5 mins

SECRET_KEY = os.environ.get("SECRET_KEY", "vYSrDoqfBF")

for k, v in os.environ.items():
    if k == "DATABASE_URL":
        SQLALCHEMY_DATABASE_URL = v
