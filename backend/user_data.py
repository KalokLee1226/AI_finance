import json
import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user


router = APIRouter(prefix="/api")


class CommoditiesUpdate(BaseModel):
  commodities: List[str]


DEFAULT_COMMODITIES = ["gold", "oil", "silver"]


@router.get("/me")
async def get_profile(current_user: str = Depends(get_current_user)):
  return {"username": current_user}


@router.get("/user-commodities")
async def get_user_commodities(current_user: str = Depends(get_current_user)):
  """获取当前用户的自选品种列表。"""
  conn = sqlite3.connect("users.db")
  c = conn.cursor()
  c.execute("SELECT commodities FROM user_settings WHERE username=?", (current_user,))
  row = c.fetchone()
  conn.close()

  if row and row[0]:
    try:
      arr = json.loads(row[0])
      if isinstance(arr, list) and arr:
        return {"commodities": arr}
    except Exception:
      pass

  return {"commodities": DEFAULT_COMMODITIES}


@router.post("/user-commodities")
async def set_user_commodities(payload: CommoditiesUpdate, current_user: str = Depends(get_current_user)):
  """更新当前用户的自选品种列表。"""
  # 简单过滤：只保留非空字符串
  cleaned = [k for k in payload.commodities if isinstance(k, str) and k]
  if not cleaned:
    cleaned = DEFAULT_COMMODITIES

  data = json.dumps(cleaned, ensure_ascii=False)

  conn = sqlite3.connect("users.db")
  c = conn.cursor()
  c.execute("SELECT 1 FROM user_settings WHERE username=?", (current_user,))
  exists = c.fetchone() is not None
  if exists:
    c.execute("UPDATE user_settings SET commodities=? WHERE username=?", (data, current_user))
  else:
    c.execute("INSERT INTO user_settings (username, commodities) VALUES (?, ?)", (current_user, data))
  conn.commit()
  conn.close()

  return {"status": "success"}
