from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProjectCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: str = "Argentina"
    valor_total: Decimal = Decimal(0)
    monto_objetivo: Decimal = Decimal(0)
    retorno_anual_pct: Decimal = Decimal(0)
    periodo_meses: int = 12
    presupuesto_obra: Decimal = Decimal(0)
    imagen_url: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin_estimada: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    status: Optional[str] = None
    monto_recaudado: Optional[Decimal] = None
    avance_fisico_pct: Optional[Decimal] = None
    costo_ejecutado: Optional[Decimal] = None
    retorno_anual_pct: Optional[Decimal] = None
    imagen_url: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    ubicacion: Optional[str]
    ciudad: Optional[str]
    pais: str
    valor_total: Decimal
    monto_objetivo: Decimal
    monto_recaudado: Decimal
    retorno_anual_pct: Decimal
    periodo_meses: int
    status: str
    avance_fisico_pct: Decimal
    presupuesto_obra: Decimal
    costo_ejecutado: Decimal
    imagen_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    investor_id: int
    project_id: int
    monto_comprometido: Decimal
    monto_integrado: Decimal = Decimal(0)
    precio_participacion: Decimal = Decimal(1)
    notas: Optional[str] = None
    comprobante_ref: Optional[str] = None


class SubscriptionOut(BaseModel):
    id: int
    investor_id: int
    project_id: int
    monto_comprometido: Decimal
    monto_integrado: Decimal
    cantidad_participaciones: Decimal
    status: str
    notas: Optional[str]
    comprobante_ref: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
