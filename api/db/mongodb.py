"""
Cliente de MongoDB.

Implementa una conexión singleton: se crea UNA sola instancia
del cliente al iniciar el API y se reutiliza para todos los requests.
Esto es mucho más eficiente que abrir/cerrar conexión en cada llamada.
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

from api.config import settings


class MongoDB:
    """Wrapper de MongoDB con manejo de conexión."""

    client: MongoClient | None = None
    db: Database | None = None

    @classmethod
    def connect(cls) -> None:
        """Abre la conexión a MongoDB. Se llama una vez al iniciar el API."""
        try:
            cls.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000,  # falla rápido si no hay BD
            )
            # Forzar conexión real (MongoClient es lazy por defecto)
            cls.client.admin.command("ping")
            cls.db = cls.client[settings.MONGO_DB]
            print(f"✅ MongoDB conectado a {settings.MONGO_DB}")
        except ServerSelectionTimeoutError as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        """Cierra la conexión. Se llama al apagar el API."""
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB desconectado")

    @classmethod
    def get_collection(cls, name: str):
        """Obtiene una colección por nombre. Útil en los routers."""
        if cls.db is None:
            raise RuntimeError(
                "MongoDB no está conectado. Llama a MongoDB.connect() primero."
            )
        return cls.db[name]
