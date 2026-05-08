"""
Utilidades para serializar datos de MongoDB y Cassandra a JSON.

Power BI y la mayoría de clientes esperan tipos primitivos (str, int, float, bool).
Las BDs devuelven tipos especiales que necesitan conversión:

- MongoDB: ObjectId, datetime, Decimal128
- Cassandra: Date, Time, Decimal, UUID, datetime

Estos helpers normalizan todo a tipos serializables.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from bson import ObjectId


def serialize_value(value: Any) -> Any:
    """Convierte UN valor a un tipo JSON-serializable."""
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return serialize_doc(value)
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    return value


def serialize_doc(doc: dict) -> dict:
    """Convierte un documento entero (todos sus campos) a JSON-friendly."""
    return {key: serialize_value(val) for key, val in doc.items()}


def serialize_docs(docs: list[dict]) -> list[dict]:
    """Convierte una lista de documentos."""
    return [serialize_doc(doc) for doc in docs]
