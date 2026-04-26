from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nombre: str
    apellido: str
    email: str
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str
    password: str
    role: str = "inversor"


class UserOut(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
