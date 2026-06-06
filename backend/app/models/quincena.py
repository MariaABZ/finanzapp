import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Date, DateTime, Integer, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Quincena(Base):
    __tablename__ = "quincenas"
    __table_args__ = (
        UniqueConstraint("user_id", "anio", "mes", "numero", name="uq_quincena_usuario"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    ingresos: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="quincenas")
    gastos: Mapped[list["Gasto"]] = relationship("Gasto", back_populates="quincena", cascade="all, delete-orphan")
    deudas: Mapped[list["Deuda"]] = relationship("Deuda", back_populates="quincena", cascade="all, delete-orphan")
