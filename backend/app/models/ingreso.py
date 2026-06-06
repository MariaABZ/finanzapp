import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, ForeignKey, Numeric, DateTime, Integer, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class TipoIngreso(str, Enum):
    SALARIO = "salario"
    FREELANCE = "freelance"
    NEGOCIO = "negocio"
    ARRIENDO_RECIBIDO = "arriendo_recibido"
    PENSION = "pension"
    OTRO = "otro"

class IngresoMensual(Base):
    __tablename__ = "ingresos_mensuales"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoIngreso] = mapped_column(SAEnum(TipoIngreso), nullable=False)
    monto_mensual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    porcentaje_primera_quincena: Mapped[int] = mapped_column(Integer, default=50)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="ingresos_mensuales")
