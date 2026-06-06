from datetime import date
from sqlalchemy.orm import Session
from app.models.deuda import Deuda, EstadoDeuda

def clasificar_urgencia(fecha_vencimiento: date, hoy: date) -> str:
    dias = (fecha_vencimiento - hoy).days
    if dias <= 0:
        return "urgente"
    elif dias <= 3:
        return "proximo"
    return "a_tiempo"

def obtener_recordatorios(db: Session, user_id: str, hoy: date = None) -> list[dict]:
    if hoy is None:
        hoy = date.today()
    deudas = (
        db.query(Deuda)
        .join(Deuda.quincena)
        .filter(
            Deuda.quincena.has(user_id=user_id),
            Deuda.estado == EstadoDeuda.PENDIENTE,
        )
        .order_by(Deuda.fecha_vencimiento)
        .all()
    )
    return [
        {
            "id": str(d.id),
            "entidad": d.entidad,
            "descripcion": d.descripcion,
            "monto": float(d.monto),
            "fecha_vencimiento": d.fecha_vencimiento.isoformat(),
            "urgencia": clasificar_urgencia(d.fecha_vencimiento, hoy),
            "quincena_id": str(d.quincena_id),
        }
        for d in deudas
    ]
