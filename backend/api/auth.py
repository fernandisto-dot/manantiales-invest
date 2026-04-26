from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_current_user
from ..models.user import User
from ..schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut
from ..core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        role=user.role
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/usuarios", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "direccion", "administracion"):
        raise HTTPException(status_code=403, detail="Sin permisos")
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=data.email,
        nombre=data.nombre,
        apellido=data.apellido,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
