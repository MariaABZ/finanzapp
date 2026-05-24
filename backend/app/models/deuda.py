import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Numeric, Date, DateTime, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.user import Base


class EstadoDeuda(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"


class Deuda(Base):
    __tablename__ = "deudas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quincena_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quincenas.id"), nullable=False
    )
    entidad: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EstadoDeuda] = mapped_column(
        SAEnum(EstadoDeuda), default=EstadoDeuda.PENDIENTE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quincena: Mapped["Quincena"] = relationship("Quincena", back_populates="deudas")  # noqa: F821
