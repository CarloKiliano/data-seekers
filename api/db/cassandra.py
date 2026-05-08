"""
Cliente de Cassandra.

Igual que MongoDB: se crea UNA sesión al iniciar el API y se reutiliza.
Cassandra es especialmente costoso de inicializar (handshake con cluster),
así que esto es importante para performance.
"""

from cassandra.cluster import Cluster, Session, NoHostAvailable
from cassandra.auth import PlainTextAuthProvider

from api.config import settings


class CassandraDB:
    """Wrapper de Cassandra con manejo de sesión."""

    cluster: Cluster | None = None
    session: Session | None = None

    @classmethod
    def connect(cls) -> None:
        """Abre la sesión a Cassandra. Se llama una vez al iniciar el API."""
        try:
            # Si hay credenciales en .env, las usamos
            auth_provider = None
            if settings.CASSANDRA_USER and settings.CASSANDRA_PASSWORD:
                auth_provider = PlainTextAuthProvider(
                    username=settings.CASSANDRA_USER,
                    password=settings.CASSANDRA_PASSWORD,
                )

            cls.cluster = Cluster(
                contact_points=[settings.CASSANDRA_HOST],
                port=settings.CASSANDRA_PORT,
                auth_provider=auth_provider,
                protocol_version=5,
            )
            cls.session = cls.cluster.connect(settings.CASSANDRA_KEYSPACE)

            # Devuelve cada fila como dict en lugar de tupla
            # (mucho más fácil de serializar a JSON)
            cls.session.row_factory = lambda colnames, rows: [
                dict(zip(colnames, row)) for row in rows
            ]

            print(f"✅ Cassandra conectado a keyspace '{settings.CASSANDRA_KEYSPACE}'")
        except NoHostAvailable as e:
            print(f"❌ Error conectando a Cassandra: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        """Cierra la sesión y cluster."""
        if cls.session:
            cls.session.shutdown()
        if cls.cluster:
            cls.cluster.shutdown()
        print("🔌 Cassandra desconectado")

    @classmethod
    def get_session(cls) -> Session:
        """Obtiene la sesión activa. Útil en los routers."""
        if cls.session is None:
            raise RuntimeError(
                "Cassandra no está conectado. Llama a CassandraDB.connect() primero."
            )
        return cls.session
