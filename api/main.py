"""
Aplicación FastAPI principal.

Este es el punto de entrada del API. Aquí:
1. Se crea la app FastAPI
2. Se conectan las BDs al iniciar
3. Se registran los routers (endpoints organizados por dominio)
4. Se cierran conexiones al apagar

Para ejecutar:
    uvicorn api.main:app --reload

Documentación interactiva (auto-generada por FastAPI):
    http://localhost:8000/docs        ← Swagger UI
    http://localhost:8000/redoc       ← ReDoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.db.mongodb import MongoDB
from api.db.cassandra import CassandraDB
from api.routers import resenas, eventos, ventas, inventario, kpis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la app.

    `lifespan` reemplaza los antiguos `startup` y `shutdown` events.
    Aquí abrimos conexiones a las BDs ANTES de aceptar requests,
    y las cerramos cuando el API se apaga.
    """
    # ── Startup: conectar a las BDs ──────────────────────────
    print("\n" + "=" * 60)
    print("🚀 Iniciando API Panam NoSQL")
    print("=" * 60)
    MongoDB.connect()
    CassandraDB.connect()
    print("=" * 60)
    print(f"📚 Documentación: http://localhost:{settings.API_PORT}/docs")
    print("=" * 60 + "\n")

    yield  # ← Aquí el API ya está corriendo y atendiendo requests

    # ── Shutdown: cerrar BDs limpiamente ─────────────────────
    print("\n🛑 Apagando API...")
    MongoDB.disconnect()
    CassandraDB.disconnect()


# ── Crear la aplicación FastAPI ──────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS: permitir requests desde Power BI / browser ─────────
# Power BI Desktop hace requests directos sin CORS, pero esto es útil
# si en el futuro conectas un frontend web o Power BI Service.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En producción, restringir dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoint raíz: salud del API ─────────────────────────────
@app.get("/", tags=["Health"], summary="Endpoint raíz")
def read_root():
    """Devuelve información básica del API. Útil para verificar que está vivo."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "docs": "/docs",
        "endpoints_principales": [
            "/api/v1/resenas",
            "/api/v1/eventos",
            "/api/v1/ventas",
            "/api/v1/inventario",
            "/api/v1/kpis",
        ],
    }


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    """Verifica que las conexiones a las BDs están vivas."""
    salud = {"api": "ok", "mongodb": "?", "cassandra": "?"}

    try:
        MongoDB.client.admin.command("ping")
        salud["mongodb"] = "ok"
    except Exception as e:
        salud["mongodb"] = f"error: {e}"

    try:
        CassandraDB.session.execute("SELECT now() FROM system.local")
        salud["cassandra"] = "ok"
    except Exception as e:
        salud["cassandra"] = f"error: {e}"

    return salud


# ── Registrar todos los routers bajo /api/v1 ─────────────────
API_PREFIX = "/api/v1"

app.include_router(resenas.router, prefix=API_PREFIX)
app.include_router(eventos.router, prefix=API_PREFIX)
app.include_router(ventas.router, prefix=API_PREFIX)
app.include_router(inventario.router, prefix=API_PREFIX)
app.include_router(kpis.router, prefix=API_PREFIX)
