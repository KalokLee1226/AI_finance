from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ReportRequest(BaseModel):
    commodity: str