from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class InvestorCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    crear_usuario: bool = False
    password: Optional[str] = None


class InvestorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    status: Optional[str] = None
    kyc_documento: Optional[bool] = None
    kyc_domicilio: Optional[bool] = None
    kyc_selfie: Optional[bool] = None


class InvestorOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str]
    documento_tipo: Optional[str]
    documento_numero: Optional[str]
    pais: Optional[str]
    ciudad: Optional[str]
    status: str
    kyc_documento: bool
    kyc_domicilio: bool
    kyc_selfie: bool
    referral_code: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
