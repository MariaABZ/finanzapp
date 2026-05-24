import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Numeric, DateTime, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.user import Base


class CategoriaGasto(str, Enum):
    ARRIENDO = "arriendo"
    ALIMENTACION = "alimentacion"
    SERVICIOS = "servicios"
    TRANSPORTE = "transporte"
    SALUD = "salud"
    EDUCACION = "educacion"
    ENTRETENIMIENTO = "entretenimiento"
    OTRO = "otro"


class Gasto(Base):
    __tablename__ = "gastos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quincena_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quincenas.id"), nullable=False
    )
    categoria: Mapped[CategoriaGasto] = mapped_column(
        SAEnum(CategoriaGasto), nullable=False
    )
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quincena: Mapped["Quincena"] = relationship("Quincena", back_populates="gastos")  # noqa: F821

