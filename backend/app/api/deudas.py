from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.deuda import Deuda, EstadoDeuda
from app.models.quincena import Quincena
from app.models.user import User
from app.services.recordatorio_service import get_recordatorios

router = APIRouter()


# --- Schemas ---

class DeudaCreate(BaseModel):
    quincena_id: UUID
    entidad: str
    descripcion: str
    monto: Decimal
    fecha_vencimiento: date

    @field_validator("monto")
    @classmethod
    def monto_positivo(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class DeudaResponse(BaseModel):
    id: UUID
    quincena_id: UUID
    entidad: str
    descripcion: str
    monto: Decimal
    fecha_vencimiento: date
    estado: EstadoDeuda

    class Config:
        from_attributes = True


class DeudaUpdate(BaseModel):
    monto: Decimal | None = None
    fecha_vencimiento: date | None = None
    estado: EstadoDeuda | None = None


# --- Helpers ---

def get_quincena_del_usuario(db: Session, quincena_id: UUID, user: User) -> Quincena:
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id, Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q


# --- Endpoints ---

@router.post("/", response_model=DeudaResponse, status_code=201)
def crear_deuda(
    data: DeudaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_quincena_del_usuario(db, data.quincena_id, user)
    deuda = Deuda(**data.model_dump())
    db.add(deuda)
    db.commit()
    db.refresh(deuda)
    return deuda


@router.get("/quincena/{quincena_id}", response_model=list[DeudaResponse])
def listar_deudas(
    quincena_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_quincena_del_usuario(db, quincena_id, user)
    return db.query(Deuda).filter(Deuda.quincena_id == quincena_id).all()


@router.get("/pendientes", response_model=list[DeudaResponse])
def deudas_pendientes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Deuda)
        .join(Deuda.quincena)
        .filter(
            Deuda.estado == EstadoDeuda.PENDIENTE,
            Quincena.user_id == user.id,
        )
        .order_by(Deuda.fecha_vencimiento)
        .all()
    )


@router.get("/recordatorios")
def recordatorios(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_recordatorios(db, user)


@router.patch("/{deuda_id}", response_model=DeudaResponse)
def actualizar_deuda(
    deuda_id: UUID,
    data: DeudaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    get_quincena_del_usuario(db, deuda.quincena_id, user)
    if data.monto is not None:
        if data.monto <= 0:
            raise HTTPException(status_code=422, detail="El monto debe ser mayor a 0")
        deuda.monto = data.monto
    if data.fecha_vencimiento is not None:
        deuda.fecha_vencimiento = data.fecha_vencimiento
    if data.estado is not None:
        deuda.estado = data.estado
    db.commit()
    db.refresh(deuda)
    return deuda


@router.delete("/{deuda_id}", status_code=204)
def eliminar_deuda(
    deuda_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deuda = db.query(Deuda).filter(Deuda.id == deuda_id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    get_quincena_del_usuario(db, deuda.quincena_id, user)
    db.delete(deuda)
    db.commit()

