import calendar
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.quincena import Quincena
from app.models.user import User

router = APIRouter()


# --- Schemas ---

class QuincenaCreate(BaseModel):
    anio: int
    mes: int   # 1-12
    numero: int  # 1 o 2
    ingresos: Decimal = Decimal("0")


class QuincenaResponse(BaseModel):
    id: UUID
    anio: int
    mes: int
    numero: int
    fecha_inicio: date
    fecha_fin: date
    ingresos: Decimal

    class Config:
        from_attributes = True


class QuincenaUpdate(BaseModel):
    ingresos: Decimal


# --- Helpers ---

def calcular_fechas(anio: int, mes: int, numero: int) -> tuple[date, date]:
    if numero == 1:
        return date(anio, mes, 1), date(anio, mes, 15)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, 16), date(anio, mes, ultimo_dia)


# --- Endpoints ---

@router.post("/", response_model=QuincenaResponse, status_code=201)
def crear_quincena(
    data: QuincenaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existe = db.query(Quincena).filter(
        Quincena.user_id == user.id,
        Quincena.anio == data.anio,
        Quincena.mes == data.mes,
        Quincena.numero == data.numero,
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe esa quincena")

    inicio, fin = calcular_fechas(data.anio, data.mes, data.numero)
    quincena = Quincena(
        user_id=user.id,
        anio=data.anio,
        mes=data.mes,
        numero=data.numero,
        fecha_inicio=inicio,
        fecha_fin=fin,
        ingresos=data.ingresos,
    )
    db.add(quincena)
    db.commit()
    db.refresh(quincena)
    return quincena


@router.get("/", response_model=list[QuincenaResponse])
def listar_quincenas(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Quincena).filter(Quincena.user_id == user.id).all()


@router.get("/{quincena_id}", response_model=QuincenaResponse)
def obtener_quincena(
    quincena_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id, Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q


@router.patch("/{quincena_id}", response_model=QuincenaResponse)
def actualizar_ingresos(
    quincena_id: UUID,
    data: QuincenaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id, Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    q.ingresos = data.ingresos
    db.commit()
    db.refresh(q)
    return q


@router.delete("/{quincena_id}", status_code=204)
def eliminar_quincena(
    quincena_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id, Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    if q.gastos or q.deudas:
        raise HTTPException(status_code=400, detail="La quincena tiene gastos o deudas asociados")
    db.delete(q)
    db.commit()

