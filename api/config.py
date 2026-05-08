"""
Configuración centralizada del API.

Lee variables desde el archivo .env (en la raíz del proyecto)
y las expone como un objeto `settings` que cualquier módulo puede importar.

Esto evita tener credenciales hardcodeadas y permite cambiar configuración
sin tocar código.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Buscar .env en la raíz del proyecto (sube directorios desde este archivo)
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent  # api/config.py -> api/ -> raíz
_ENV_PATH = _PROJECT_ROOT / ".env"

if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)


class Settings:
    """Configuración del API leída desde variables de entorno."""

    # ── Información del API ───────────────────────────────────
    APP_NAME: str = "Panam NoSQL API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "API REST que expone datos de MongoDB y Cassandra "
        "para consumo desde Power BI y otras herramientas."
    )

    # ── MongoDB ──────────────────────────────────────────────
    MONGO_URI: str = os.getenv(
        "MONGO_URI", "mongodb://admin:password@localhost:27017/"
    )
    MONGO_DB: str = os.getenv("MONGO_DB", "panam_nosql")

    # ── Cassandra ────────────────────────────────────────────
    CASSANDRA_HOST: str = os.getenv("CASSANDRA_HOST", "localhost")
    CASSANDRA_PORT: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    CASSANDRA_KEYSPACE: str = os.getenv("CASSANDRA_KEYSPACE", "panam_nosql")
    CASSANDRA_USER: str | None = os.getenv("CASSANDRA_USER")
    CASSANDRA_PASSWORD: str | None = os.getenv("CASSANDRA_PASSWORD")

    # ── Servidor API ─────────────────────────────────────────
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))


# Instancia única que el resto del API importa
settings = Settings()
