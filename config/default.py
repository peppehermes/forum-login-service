import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
LOG_CONFIG = os.path.join(BASE_DIR, "config_logging.yml")

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"
APP_NAME = "Login OTP App"

AUTH_OTP_THRESHOLD_SECONDS = 300  # OTPs are valid for 5 mins

SECRET_KEY = os.environ.get("SECRET_KEY", "vYSrDoqfBF")

for k, v in os.environ.items():
    if k == "DATABASE_URL":
        SQLALCHEMY_DATABASE_URL = v
