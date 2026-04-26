from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class InvestorStatus(str):
    BORRADOR = "borrador"
    INCOMPLETO = "incompleto"
    VALIDADO = "validado"
    BLOQUEADO = "bloqueado"


class Investor(Base):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)

    # Datos personales
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefono = Column(String(50))
    documento_tipo = Column(String(20))  # DNI, CUIT, Pasaporte
    documento_numero = Column(String(50))
    pais = Column(String(100))
    ciudad = Column(String(100))
    direccion = Column(Text)
    notas = Column(Text)

    # Estado del legajo
    status = Column(String(30), default="borrador")
    kyc_documento = Column(Boolean, default=False)
    kyc_domicilio = Column(Boolean, default=False)
    kyc_selfie = Column(Boolean, default=False)

    # Código de referido
    referral_code = Column(String(20), unique=True)
    referred_by = Column(Integer, ForeignKey("investors.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="investor")
    subscriptions = relationship("Subscription", back_populates="investor")
    holdings = relationship("Holding", back_populates="investor")
