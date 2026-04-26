from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .core.security import hash_password
from .models import User, Investor, Project, Subscription, Holding, AuditLog
from .api import auth, investors, projects

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS — permite que el frontend web consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringir al dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(investors.router, prefix="/api")
app.include_router(projects.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/api/dashboard/stats")
def dashboard_stats(db: Session = None):
    """Stats globales para el panel admin."""
    db = SessionLocal()
    try:
        from .models.ledger import Holding
        from sqlalchemy import func
        total_inversores = db.query(User).filter(User.role == "inversor").count()
        total_proyectos = db.query(Project).count()
        proyectos_activos = db.query(Project).filter(Project.status == "activo").count()
        total_recaudado = db.query(func.sum(Project.monto_recaudado)).scalar() or 0
        return {
            "total_inversores": total_inversores,
            "total_proyectos": total_proyectos,
            "proyectos_activos": proyectos_activos,
            "total_recaudado": float(total_recaudado)
        }
    finally:
        db.close()


# ── Seed: crear admin inicial si no existe ──
def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.FIRST_ADMIN_EMAIL).first()
        if not existing:
            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                nombre="Admin",
                apellido="Manantiales",
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {settings.FIRST_ADMIN_EMAIL}")
    finally:
        db.close()


seed_admin()
