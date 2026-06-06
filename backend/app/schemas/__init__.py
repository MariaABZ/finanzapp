from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from app.models.gasto import CategoriaGasto
from app.models.deuda import EstadoDeuda
from app.models.ingreso import TipoIngreso

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True

class QuincenaCreate(BaseModel):
    anio: int = Field(ge=2000, le=2100)
    mes: int = Field(ge=1, le=12)
    numero: int = Field(ge=1, le=2)
    ingresos: Decimal = Field(default=Decimal("0"), ge=0)

class QuincenaUpdate(BaseModel):
    ingresos: Decimal = Field(ge=0)

class QuincenaOut(BaseModel):
    id: str
    anio: int
    mes: int
    numero: int
    fecha_inicio: date
    fecha_fin: date
    ingresos: Decimal
    created_at: datetime
    class Config:
        from_attributes = True

class GastoCreate(BaseModel):
    quincena_id: str
    categoria: CategoriaGasto
    descripcion: str = Field(min_length=1, max_length=255)
    monto: Decimal = Field(gt=0)

class GastoOut(BaseModel):
    id: str
    quincena_id: str
    categoria: CategoriaGasto
    descripcion: str
    monto: Decimal
    created_at: datetime
    class Config:
        from_attributes = True

class DeudaCreate(BaseModel):
    quincena_id: str
    entidad: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1, max_length=255)
    monto: Decimal = Field(gt=0)
    fecha_vencimiento: date

class DeudaUpdate(BaseModel):
    estado: EstadoDeuda

class DeudaOut(BaseModel):
    id: str
    quincena_id: str
    entidad: str
    descripcion: str
    monto: Decimal
    fecha_vencimiento: date
    estado: EstadoDeuda
    created_at: datetime
    class Config:
        from_attributes = True

class IngresoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    tipo: TipoIngreso
    monto_mensual: Decimal = Field(gt=0)
    porcentaje_primera_quincena: int = Field(default=50, ge=0, le=100)

class IngresoUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=255)
    monto_mensual: Decimal | None = Field(default=None, gt=0)
    porcentaje_primera_quincena: int | None = Field(default=None, ge=0, le=100)
    activo: bool | None = None

class IngresoOut(BaseModel):
    id: str
    nombre: str
    tipo: TipoIngreso
    monto_mensual: Decimal
    porcentaje_primera_quincena: int
    activo: bool
    created_at: datetime
    class Config:
        from_attributes = True

class RecordatorioOut(BaseModel):
    id: str
    entidad: str
    descripcion: str
    monto: float
    fecha_vencimiento: str
    urgencia: str
    quincena_id: str
