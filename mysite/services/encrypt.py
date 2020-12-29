import jwt
from decouple import config


class Encrypt:
    """[contains methods for encoding token with id and decoding existing token]

    Returns:
        [encode or decode result]: [token or payload]
    """
    @staticmethod
    def decode(token):
        return jwt.decode(token, config('ENCODE_SECRET_KEY'), algorithms=["HS256"])

    @staticmethod
    def encode(user_id):
        return jwt.encode({"id": user_id}, config('ENCODE_SECRET_KEY'), algorithm="HS256").decode('utf-8')
