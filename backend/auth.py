from fastapi import APIRouter, HTTPException, Depends, Header
import sqlite3
from typing import Optional

from models import RegisterRequest, LoginRequest
from utils import hash_password, create_token, verify_token

router = APIRouter(prefix="/api")


# 注册接口
@router.post("/register")
async def register(req: RegisterRequest):

    if len(req.username) < 3 or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="用户名至少3个字符，密码至少6个字符")

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (req.username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed_pw, salt = hash_password(req.password)

    # 注册时同时写入邮箱信息（用于后续邮箱告警推送）
    c.execute(
        "INSERT INTO users (username, password, salt, email) VALUES (?, ?, ?, ?)",
        (req.username, hashed_pw, salt, req.email)
    )

    conn.commit()
    conn.close()

    return {"status": "success", "message": "注册成功，请登录"}


# 登录接口
@router.post("/login")
async def login(req: LoginRequest):

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT password, salt FROM users WHERE username=?", (req.username,))
    row = c.fetchone()

    conn.close()

    if row:
        stored_hash, salt = row

        if hash_password(req.password, salt)[0] == stored_hash:
            token = create_token(req.username)
            return {"status": "success", "message": "登录成功", "token": token}

    raise HTTPException(status_code=401, detail="用户名或密码错误")


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """从 Authorization: Bearer <token> 头中解析并验证当前用户。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效认证信息")

    token = authorization[7:]
    try:
        username = verify_token(token)
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="认证失败，请重新登录")
