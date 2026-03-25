from typing import Optional, List

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class ReportRequest(BaseModel):
    commodity: str
    # 预设人物 key，例如：default / buffett / soros / dalio / custom
    persona: Optional[str] = None
    # 当 persona = "custom" 时，用户自定义人物名称（如“某某股神”）
    custom_persona_name: Optional[str] = None
    # 当 persona = "custom" 时的详细人设说明和风格提示词
    custom_persona_prompt: Optional[str] = None
    # 报告生成模式：detailed=详尽版（默认），fast=快速版（结构精简、返回更短）
    mode: Optional[str] = "detailed"


class ChatMessage(BaseModel):
    role: str  # "user" / "assistant" / "system"
    content: str


class ChatRequest(BaseModel):
    # 用户当前关注的标的（可选，用于给模型上下文）
    commodity: Optional[str] = None
    # 本轮提问内容
    question: str
    # 人物/风格，与 ReportRequest 保持一致
    persona: Optional[str] = None
    custom_persona_name: Optional[str] = None
    custom_persona_prompt: Optional[str] = None
    # 前端传入的历史对话，用于多轮追问
    history: Optional[List[ChatMessage]] = None