from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Subscription(Base):
    """Registro de cada suscripción de un inversor a un proyecto."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Montos
    monto_comprometido = Column(Numeric(18, 2), nullable=False)  # Lo que prometió aportar
    monto_integrado = Column(Numeric(18, 2), default=0)          # Lo que efectivamente pagó
    precio_participacion = Column(Numeric(18, 2), default=1)     # Precio de la participación
    cantidad_participaciones = Column(Numeric(18, 6), default=0) # Cantidad emitida

    # Estado
    status = Column(String(30), default="pendiente")
    # pendiente | integrado | parcial | cancelado

    # Notas y comprobante
    notas = Column(Text)
    comprobante_ref = Column(String(200))  # Nro de transferencia, cheque, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relaciones
    investor = relationship("Investor", back_populates="subscriptions")
    project = relationship("Project", back_populates="subscriptions")


class Holding(Base):
    """Posición actual de cada inversor en cada proyecto (cap table)."""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    participaciones = Column(Numeric(18, 6), default=0)  # Tenencia actual
    valor_invertido = Column(Numeric(18, 2), default=0)  # Capital integrado total
    retorno_acumulado = Column(Numeric(18, 2), default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investor = relationship("Investor", back_populates="holdings")
    project = relationship("Project", back_populates="holdings")


class AuditLog(Base):
    """Bitácora de todas las acciones del sistema."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100))   # nombre de la tabla afectada
    entity_id = Column(Integer)
    detail = Column(Text)
    ip = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
