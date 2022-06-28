import pyotp

import config


class TOTPManager:
    @staticmethod
    def generate_secret():
        """ Function for generating a secret for TOTP algorithm """
        return pyotp.random_base32()

    @staticmethod
    def generate_otp(secret):
        """ Function for generating time-based OTP """
        totp = pyotp.TOTP(secret, interval=config.AUTH_OTP_THRESHOLD_SECONDS)
        return totp.now()

    @staticmethod
    def validate_otp(otp, secret):
        """ Function for validating time-based OTP """
        totp = pyotp.TOTP(secret)
        return totp.verify(otp)
