from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.quincenas import router as quincenas_router
from app.api.finanzas import router as finanzas_router
from app.api.ingresos import router as ingresos_router

app = FastAPI(title="FinanzApp", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(quincenas_router, prefix="/quincenas", tags=["quincenas"])
app.include_router(finanzas_router, tags=["finanzas"])
app.include_router(ingresos_router, prefix="/ingresos", tags=["ingresos"])

@app.get("/health")
def health():
    return {"status": "ok"}
