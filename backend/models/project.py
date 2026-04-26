from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    ubicacion = Column(String(200))
    ciudad = Column(String(100))
    pais = Column(String(100), default="Argentina")

    # Financiero
    valor_total = Column(Numeric(18, 2), default=0)       # Capital total del proyecto
    monto_objetivo = Column(Numeric(18, 2), default=0)    # Monto a financiar
    monto_recaudado = Column(Numeric(18, 2), default=0)   # Monto ya suscripto
    retorno_anual_pct = Column(Numeric(5, 2), default=0)  # % retorno anual estimado
    periodo_meses = Column(Integer, default=12)            # Duración en meses

    # Estado
    status = Column(String(30), default="borrador")
    # borrador | activo | financiado | en_obra | finalizado | cancelado

    # Obra
    avance_fisico_pct = Column(Numeric(5, 2), default=0)
    presupuesto_obra = Column(Numeric(18, 2), default=0)
    costo_ejecutado = Column(Numeric(18, 2), default=0)

    # Imagen
    imagen_url = Column(String(500))

    # Fechas
    fecha_inicio = Column(DateTime)
    fecha_fin_estimada = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    subscriptions = relationship("Subscription", back_populates="project")
    holdings = relationship("Holding", back_populates="project")
