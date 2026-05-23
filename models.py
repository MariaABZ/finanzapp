import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, ForeignKey, Numeric, Date, DateTime, Integer, Enum as SAEnum, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ingresos_mensuales: Mapped[list["IngresoMensual"]] = relationship("IngresoMensual", back_populates="user")
    quincenas: Mapped[list["Quincena"]] = relationship("Quincena", back_populates="user")


class TipoIngreso(str, Enum):
    SALARIO = "salario"
    FREELANCE = "freelance"
    NEGOCIO = "negocio"
    ARRIENDO_RECIBIDO = "arriendo_recibido"
    PENSION = "pension"
    OTRO = "otro"


class IngresoMensual(Base):
    """
    Fuente de ingreso mensual del usuario.
    Puede ser salario, freelance, negocio, etc.
    Se usa para calcular automáticamente el ingreso de cada quincena (50% por defecto).
    """
    __tablename__ = "ingresos_mensuales"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)           # "Salario Empresa X"
    tipo: Mapped[TipoIngreso] = mapped_column(SAEnum(TipoIngreso), nullable=False)
    monto_mensual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Porcentaje que llega en la primera quincena (0-100). El resto va a la segunda.
    porcentaje_primera_quincena: Mapped[int] = mapped_column(Integer, default=50)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="ingresos_mensuales")


class Quincena(Base):
    __tablename__ = "quincenas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)          # 1-12
    numero: Mapped[int] = mapped_column(Integer, nullable=False)       # 1 o 2 (primera o segunda quincena)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    # Ingreso real recibido esta quincena (puede diferir del calculado automáticamente)
    ingresos: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="quincenas")
    gastos: Mapped[list["Gasto"]] = relationship("Gasto", back_populates="quincena")
    deudas: Mapped[list["Deuda"]] = relationship("Deuda", back_populates="quincena")


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

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quincena_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quincenas.id"), nullable=False)
    categoria: Mapped[CategoriaGasto] = mapped_column(SAEnum(CategoriaGasto), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quincena: Mapped["Quincena"] = relationship("Quincena", back_populates="gastos")


class EstadoDeuda(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"


class Deuda(Base):
    __tablename__ = "deudas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quincena_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quincenas.id"), nullable=False)
    entidad: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EstadoDeuda] = mapped_column(SAEnum(EstadoDeuda), default=EstadoDeuda.PENDIENTE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quincena: Mapped["Quincena"] = relationship("Quincena", back_populates="deudas")
