import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.user import Base


class Quincena(Base):
    __tablename__ = "quincenas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)      # 1-12
    numero: Mapped[int] = mapped_column(Integer, nullable=False)   # 1 o 2
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    ingresos: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="quincenas")  # noqa: F821
    gastos: Mapped[list["Gasto"]] = relationship("Gasto", back_populates="quincena")  # noqa: F821
    deudas: Mapped[list["Deuda"]] = relationship("Deuda", back_populates="quincena")  # noqa: F821
