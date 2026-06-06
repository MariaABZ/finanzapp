from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.ingreso import IngresoMensual
from app.schemas import IngresoCreate, IngresoUpdate, IngresoOut

router = APIRouter()

@router.post("/", response_model=IngresoOut, status_code=201)
def crear_ingreso(body: IngresoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ingreso = IngresoMensual(**body.model_dump(), user_id=user.id)
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)
    return ingreso

@router.get("/", response_model=list[IngresoOut])
def listar_ingresos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(IngresoMensual).filter(IngresoMensual.user_id == user.id, IngresoMensual.activo == True).all()

@router.patch("/{ingreso_id}", response_model=IngresoOut)
def actualizar_ingreso(ingreso_id: str, body: IngresoUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ingreso = db.query(IngresoMensual).filter(IngresoMensual.id == ingreso_id, IngresoMensual.user_id == user.id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(ingreso, field, value)
    db.commit()
    db.refresh(ingreso)
    return ingreso

@router.delete("/{ingreso_id}", status_code=204)
def desactivar_ingreso(ingreso_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ingreso = db.query(IngresoMensual).filter(IngresoMensual.id == ingreso_id, IngresoMensual.user_id == user.id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    ingreso.activo = False
    db.commit()
