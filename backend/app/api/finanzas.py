from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.quincena import Quincena
from app.models.gasto import Gasto
from app.models.deuda import Deuda, EstadoDeuda
from app.schemas import GastoCreate, GastoOut, DeudaCreate, DeudaOut, DeudaUpdate, RecordatorioOut
from app.services.recordatorio_service import obtener_recordatorios

router = APIRouter()

def _quincena_del_usuario(db, quincena_id, user_id):
    q = db.query(Quincena).filter(Quincena.id == quincena_id, Quincena.user_id == user_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q

@router.post("/gastos", response_model=GastoOut, status_code=201)
def crear_gasto(body: GastoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _quincena_del_usuario(db, body.quincena_id, str(user.id))
    gasto = Gasto(**body.model_dump())
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto

@router.get("/gastos", response_model=list[GastoOut])
def listar_gastos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Gasto).join(Gasto.quincena).filter(Quincena.user_id == user.id).all()

@router.delete("/gastos/{gasto_id}", status_code=204)
def eliminar_gasto(gasto_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    gasto = db.query(Gasto).join(Gasto.quincena).filter(Gasto.id == gasto_id, Quincena.user_id == user.id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    db.delete(gasto)
    db.commit()

@router.post("/deudas", response_model=DeudaOut, status_code=201)
def crear_deuda(body: DeudaCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _quincena_del_usuario(db, body.quincena_id, str(user.id))
    deuda = Deuda(**body.model_dump())
    db.add(deuda)
    db.commit()
    db.refresh(deuda)
    return deuda

@router.get("/deudas", response_model=list[DeudaOut])
def listar_deudas(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Deuda).join(Deuda.quincena).filter(Quincena.user_id == user.id).all()

@router.patch("/deudas/{deuda_id}", response_model=DeudaOut)
def actualizar_deuda(deuda_id: str, body: DeudaUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deuda = db.query(Deuda).join(Deuda.quincena).filter(Deuda.id == deuda_id, Quincena.user_id == user.id).first()
    if not deuda:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    deuda.estado = body.estado
    db.commit()
    db.refresh(deuda)
    return deuda

@router.get("/recordatorios", response_model=list[RecordatorioOut])
def listar_recordatorios(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return obtener_recordatorios(db, str(user.id))
