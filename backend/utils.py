import hashlib
import hmac
import os
import time
import base64
import json


def hash_password(password: str, salt=None):

    if not salt:
        salt = os.urandom(16).hex()

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()

    return hashed, salt


# 简单的 HMAC Token 实现（避免额外依赖），仅在本项目内使用
SECRET_KEY = os.getenv("AI_FINANCE_SECRET", "change-this-secret-key")


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(username: str, expires_in: int = 7 * 24 * 3600) -> str:
    """生成包含用户名和过期时间的签名 Token。"""
    payload = {"u": username, "exp": int(time.time()) + expires_in}
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(SECRET_KEY.encode(), raw, hashlib.sha256).digest()
    return f"{_b64_encode(raw)}.{_b64_encode(sig)}"


def verify_token(token: str) -> str:
    """验证 Token，返回用户名；失败则抛出 ValueError。"""
    try:
        payload_b64, sig_b64 = token.split(".", 1)
    except ValueError:
        raise ValueError("Invalid token format")

    raw = _b64_decode(payload_b64)
    sig = _b64_decode(sig_b64)
    expected_sig = hmac.new(SECRET_KEY.encode(), raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Invalid token signature")

    data = json.loads(raw.decode())
    if data.get("exp", 0) < int(time.time()):
        raise ValueError("Token expired")

    username = data.get("u")
    if not username:
        raise ValueError("Invalid token payload")
    return username
