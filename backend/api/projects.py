from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from ..core.database import get_db
from ..core.security import get_current_user, require_admin
from ..models.project import Project
from ..models.ledger import Subscription, Holding
from ..models.investor import Investor
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, SubscriptionCreate, SubscriptionOut

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])


@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.post("/", response_model=ProjectOut)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


# ── SUSCRIPCIONES ──

@router.post("/{project_id}/suscripciones", response_model=SubscriptionOut)
def create_subscription(project_id: int, data: SubscriptionCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    investor = db.query(Investor).filter(Investor.id == data.investor_id).first()
    if not investor:
        raise HTTPException(status_code=404, detail="Inversor no encontrado")

    # Calcular participaciones
    precio = data.precio_participacion if data.precio_participacion else Decimal(1)
    cantidad = data.monto_integrado / precio if precio > 0 else Decimal(0)

    sub = Subscription(
        investor_id=data.investor_id,
        project_id=project_id,
        monto_comprometido=data.monto_comprometido,
        monto_integrado=data.monto_integrado,
        precio_participacion=precio,
        cantidad_participaciones=cantidad,
        notas=data.notas,
        comprobante_ref=data.comprobante_ref,
        status="integrado" if data.monto_integrado >= data.monto_comprometido else "parcial",
        created_by=current_user.id
    )
    db.add(sub)

    # Actualizar monto recaudado del proyecto
    project.monto_recaudado = (project.monto_recaudado or Decimal(0)) + data.monto_integrado

    # Actualizar o crear holding
    holding = db.query(Holding).filter(
        Holding.investor_id == data.investor_id,
        Holding.project_id == project_id
    ).first()
    if holding:
        holding.participaciones += cantidad
        holding.valor_invertido += data.monto_integrado
    else:
        holding = Holding(
            investor_id=data.investor_id,
            project_id=project_id,
            participaciones=cantidad,
            valor_invertido=data.monto_integrado
        )
        db.add(holding)

    db.commit()
    db.refresh(sub)
    return sub


@router.get("/{project_id}/suscripciones", response_model=List[SubscriptionOut])
def list_subscriptions(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Subscription).filter(Subscription.project_id == project_id).all()


@router.get("/{project_id}/cap-table")
def cap_table(project_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    holdings = db.query(Holding).filter(Holding.project_id == project_id).all()
    project = db.query(Project).filter(Project.id == project_id).first()
    total = sum(h.participaciones for h in holdings) or Decimal(1)

    result = []
    for h in holdings:
        inv = db.query(Investor).filter(Investor.id == h.investor_id).first()
        result.append({
            "inversor": f"{inv.nombre} {inv.apellido}" if inv else "—",
            "email": inv.email if inv else "—",
            "participaciones": float(h.participaciones),
            "valor_invertido": float(h.valor_invertido),
            "pct_tenencia": float(h.participaciones / total * 100)
        })

    return {
        "proyecto": project.nombre if project else "—",
        "total_recaudado": float(project.monto_recaudado) if project else 0,
        "cap_table": sorted(result, key=lambda x: x["valor_invertido"], reverse=True)
    }
