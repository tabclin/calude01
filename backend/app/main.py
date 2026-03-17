"""
Ponto de entrada da API — FastAPI.
Registra todos os routers e configura CORS, docs e lifecycle.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import dashboard, patients, products, transactions, expenses, goals


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas se ainda não existirem (dev only — em prod use migrations)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de análise gerencial para clínicas de saúde e estética.",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(dashboard.router,    prefix=f"{API_PREFIX}/dashboard",    tags=["Dashboard"])
app.include_router(patients.router,     prefix=f"{API_PREFIX}/patients",      tags=["Pacientes"])
app.include_router(products.router,     prefix=f"{API_PREFIX}/products",      tags=["Produtos/Serviços"])
app.include_router(transactions.router, prefix=f"{API_PREFIX}/transactions",  tags=["Transações"])
app.include_router(expenses.router,     prefix=f"{API_PREFIX}/expenses",      tags=["Gastos"])
app.include_router(goals.router,        prefix=f"{API_PREFIX}/goals",         tags=["Metas"])


@app.get("/health", tags=["Saúde"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
