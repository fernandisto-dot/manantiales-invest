from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random, string
from ..core.database import get_db
from ..core.security import get_current_user, require_admin, hash_password
from ..models.investor import Investor
from ..models.user import User
from ..schemas.investor import InvestorCreate, InvestorUpdate, InvestorOut

router = APIRouter(prefix="/inversores", tags=["Inversores"])


def gen_referral_code(nombre: str) -> str:
    prefix = nombre[:3].upper()
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"MAN-{prefix}{suffix}"


@router.get("/", response_model=List[InvestorOut])
def list_investors(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "inversor":
        # Un inversor solo ve su propio perfil
        inv = db.query(Investor).filter(Investor.user_id == current_user.id).all()
        return inv
    return db.query(Investor).order_by(Investor.created_at.desc()).all()


@router.get("/{investor_id}", response_model=InvestorOut)
def get_investor(investor_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.query(Investor).filter(Investor.id == investor_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inversor no encontrado")
    if current_user.role == "inversor" and inv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")
    return inv


@router.post("/", response_model=InvestorOut)
def create_investor(data: InvestorCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    existing = db.query(Investor).filter(Investor.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado como inversor")

    user_id = None
    if data.crear_usuario and data.password:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if not existing_user:
            new_user = User(
                email=data.email,
                nombre=data.nombre,
                apellido=data.apellido,
                hashed_password=hash_password(data.password),
                role="inversor"
            )
            db.add(new_user)
            db.flush()
            user_id = new_user.id
        else:
            user_id = existing_user.id

    inv = Investor(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        telefono=data.telefono,
        documento_tipo=data.documento_tipo,
        documento_numero=data.documento_numero,
        pais=data.pais,
        ciudad=data.ciudad,
        direccion=data.direccion,
        notas=data.notas,
        user_id=user_id,
        referral_code=gen_referral_code(data.nombre)
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.put("/{investor_id}", response_model=InvestorOut)
def update_investor(investor_id: int, data: InvestorUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.query(Investor).filter(Investor.id == investor_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inversor no encontrado")
    if current_user.role == "inversor" and inv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)
    db.commit()
    db.refresh(inv)
    return inv


@router.delete("/{investor_id}")
def delete_investor(investor_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    inv = db.query(Investor).filter(Investor.id == investor_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inversor no encontrado")
    db.delete(inv)
    db.commit()
    return {"ok": True}
