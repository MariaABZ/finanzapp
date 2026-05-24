from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.gasto import Gasto, CategoriaGasto
from app.models.quincena import Quincena
from app.models.user import User

router = APIRouter()


# --- Schemas ---

class GastoCreate(BaseModel):
    quincena_id: UUID
    categoria: CategoriaGasto
    descripcion: str
    monto: Decimal

    @field_validator("monto")
    @classmethod
    def monto_positivo(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class GastoResponse(BaseModel):
    id: UUID
    quincena_id: UUID
    categoria: CategoriaGasto
    descripcion: str
    monto: Decimal

    class Config:
        from_attributes = True


class GastoUpdate(BaseModel):
    descripcion: str | None = None
    monto: Decimal | None = None


# --- Helpers ---

def get_quincena_del_usuario(db: Session, quincena_id: UUID, user: User) -> Quincena:
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id, Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q


# --- Endpoints ---

@router.post("/", response_model=GastoResponse, status_code=201)
def crear_gasto(
    data: GastoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_quincena_del_usuario(db, data.quincena_id, user)
    gasto = Gasto(**data.model_dump())
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto


@router.get("/quincena/{quincena_id}", response_model=list[GastoResponse])
def listar_gastos(
    quincena_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_quincena_del_usuario(db, quincena_id, user)
    return db.query(Gasto).filter(Gasto.quincena_id == quincena_id).all()


@router.get("/quincena/{quincena_id}/resumen")
def resumen_por_categoria(
    quincena_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_quincena_del_usuario(db, quincena_id, user)
    gastos = db.query(Gasto).filter(Gasto.quincena_id == quincena_id).all()
    resumen: dict[str, Decimal] = {}
    for g in gastos:
        resumen[g.categoria.value] = resumen.get(g.categoria.value, Decimal("0")) + g.monto
    return resumen


@router.patch("/{gasto_id}", response_model=GastoResponse)
def actualizar_gasto(
    gasto_id: UUID,
    data: GastoUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    get_quincena_del_usuario(db, gasto.quincena_id, user)
    if data.descripcion is not None:
        gasto.descripcion = data.descripcion
    if data.monto is not None:
        if data.monto <= 0:
            raise HTTPException(status_code=422, detail="El monto debe ser mayor a 0")
        gasto.monto = data.monto
    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/{gasto_id}", status_code=204)
def eliminar_gasto(
    gasto_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    get_quincena_del_usuario(db, gasto.quincena_id, user)
    db.delete(gasto)
    db.commit()

