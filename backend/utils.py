import hashlib
import os

def hash_password(password: str, salt=None):

    if not salt:
        salt = os.urandom(16).hex()

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()

    return hashed, salt