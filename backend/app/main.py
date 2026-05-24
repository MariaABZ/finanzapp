from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, quincenas, gastos, deudas

app = FastAPI(
    title="FinanzApp",
    description="API de gestión de finanzas personales quincenales",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(quincenas.router, prefix="/quincenas", tags=["quincenas"])
app.include_router(gastos.router, prefix="/gastos", tags=["gastos"])
app.include_router(deudas.router, prefix="/deudas", tags=["deudas"])


@app.get("/")
def root():
    return {"message": "FinanzApp API corriendo correctamente"}
