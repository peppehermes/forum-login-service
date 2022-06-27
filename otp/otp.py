import pyotp

from sql.schemas import UserCreate

DEFAULT_INTERVAL = 300


# Generate secret for each user
def generate_secret():
    return pyotp.random_base32()


# Generate OTP for user
def generate_otp(secret):
    totp = pyotp.TOTP(secret, interval=DEFAULT_INTERVAL)
    return totp.now()


# Validate received OTP for user
def validate_otp(otp, secret):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)
