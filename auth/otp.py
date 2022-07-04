import pyotp

import config


class TOTPManager:
    """Manager class for time-based OTP"""

    def __init__(self, user_secret: str):
        """Initializes TOTP manager on given user"""

        self.user_secret = user_secret
        self.totp = pyotp.TOTP(
            self.user_secret, interval=config.AUTH_OTP_THRESHOLD_SECONDS
        )

    @staticmethod
    def generate_secret():
        """Function for generating a secret for TOTP algorithm"""

        return pyotp.random_base32()

    def generate_otp(self):
        """Function for generating time-based OTP"""

        return self.totp.now()

    def validate_otp(self, otp_code):
        """Function for validating time-based OTP"""

        return self.totp.verify(otp_code)
