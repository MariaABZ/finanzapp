from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.quincena import Quincena
from app.schemas import QuincenaCreate, QuincenaUpdate, QuincenaOut
from app.services.ingreso_service import fechas_quincena

router = APIRouter()

def _get_quincena_or_404(db, quincena_id, user_id):
    q = db.query(Quincena).filter(Quincena.id == quincena_id, Quincena.user_id == user_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q

@router.post("/", response_model=QuincenaOut, status_code=201)
def crear_quincena(body: QuincenaCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inicio, fin = fechas_quincena(body.anio, body.mes, body.numero)
    q = Quincena(user_id=user.id, anio=body.anio, mes=body.mes, numero=body.numero, fecha_inicio=inicio, fecha_fin=fin, ingresos=body.ingresos)
    db.add(q)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe esa quincena para este usuario")
    db.refresh(q)
    return q

@router.get("/", response_model=list[QuincenaOut])
def listar_quincenas(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Quincena).filter(Quincena.user_id == user.id).order_by(Quincena.anio.desc(), Quincena.mes.desc(), Quincena.numero.desc()).all()

@router.get("/{quincena_id}", response_model=QuincenaOut)
def obtener_quincena(quincena_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_quincena_or_404(db, quincena_id, str(user.id))

@router.patch("/{quincena_id}", response_model=QuincenaOut)
def actualizar_ingresos(quincena_id: str, body: QuincenaUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = _get_quincena_or_404(db, quincena_id, str(user.id))
    q.ingresos = body.ingresos
    db.commit()
    db.refresh(q)
    return q

@router.delete("/{quincena_id}", status_code=204)
def eliminar_quincena(quincena_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = _get_quincena_or_404(db, quincena_id, str(user.id))
    if q.gastos or q.deudas:
        raise HTTPException(status_code=400, detail="No se puede eliminar una quincena con gastos o deudas")
    db.delete(q)
    db.commit()
