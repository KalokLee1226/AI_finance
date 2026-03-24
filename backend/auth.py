from fastapi import APIRouter, HTTPException
import sqlite3

from models import RegisterRequest, LoginRequest
from utils import hash_password

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

    c.execute(
        "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
        (req.username, hashed_pw, salt)
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
            return {"status": "success", "message": "登录成功"}

    raise HTTPException(status_code=401, detail="用户名或密码错误")