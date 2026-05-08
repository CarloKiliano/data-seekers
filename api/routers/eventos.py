"""
Endpoints de eventos web (MongoDB).

Expone la colección `eventos_web` para análisis de comportamiento del usuario:
- Tasa de conversión (carrito → compra)
- Eventos por dispositivo / navegador
- Modelos más buscados vs más comprados
"""

from fastapi import APIRouter, Query

from api.db.mongodb import MongoDB
from api.db.serializers import serialize_docs

router = APIRouter(prefix="/eventos", tags=["Eventos Web (MongoDB)"])


@router.get(
    "",
    summary="Listar eventos web",
    description="Devuelve eventos web con filtros opcionales.",
)
def listar_eventos(
    evento_tipo: str | None = Query(None, description="Tipo de evento (ej: 'compra')"),
    dispositivo: str | None = Query(
        None, description="Dispositivo (mobile / desktop / tablet)"
    ),
    limite: int = Query(1000, ge=1, le=5000),
):
    """Obtiene eventos. Power BI los usa para calcular conversión."""
    coleccion = MongoDB.get_collection("eventos_web")

    filtro = {}
    if evento_tipo:
        filtro["evento_tipo"] = evento_tipo
    if dispositivo:
        filtro["dispositivo"] = dispositivo

    cursor = coleccion.find(filtro, {"_id": 0}).limit(limite)
    return serialize_docs(list(cursor))


@router.get(
    "/conversion",
    summary="Tasa de conversión por modelo",
    description="Para KPI: % de visualizaciones que terminan en compra.",
)
def conversion_por_modelo():
    """
    Calcula conversión: (compras / vistas) por modelo.

    Power BI mostrará esto como un KPI principal.
    """
    coleccion = MongoDB.get_collection("eventos_web")

    pipeline = [
        {
            "$group": {
                "_id": "$modelo",
                "vistas": {
                    "$sum": {"$cond": [{"$eq": ["$evento_tipo", "vista"]}, 1, 0]}
                },
                "carritos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$evento_tipo", "carrito"]}, 1, 0]
                    }
                },
                "compras": {
                    "$sum": {"$cond": [{"$eq": ["$evento_tipo", "compra"]}, 1, 0]}
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "modelo": "$_id",
                "vistas": 1,
                "carritos": 1,
                "compras": 1,
                "tasa_conversion_pct": {
                    "$round": [
                        {
                            "$cond": [
                                {"$eq": ["$vistas", 0]},
                                0,
                                {"$multiply": [{"$divide": ["$compras", "$vistas"]}, 100]},
                            ]
                        },
                        2,
                    ]
                },
            }
        },
        {"$sort": {"tasa_conversion_pct": -1}},
    ]

    return serialize_docs(list(coleccion.aggregate(pipeline)))


@router.get(
    "/por-dispositivo",
    summary="Eventos por dispositivo",
    description="Para gráfica: 'Volumen de eventos por dispositivo'.",
)
def eventos_por_dispositivo():
    """Agrupa eventos por dispositivo y tipo."""
    coleccion = MongoDB.get_collection("eventos_web")

    pipeline = [
        {
            "$group": {
                "_id": {"dispositivo": "$dispositivo", "evento_tipo": "$evento_tipo"},
                "total": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "dispositivo": "$_id.dispositivo",
                "evento_tipo": "$_id.evento_tipo",
                "total": 1,
            }
        },
        {"$sort": {"total": -1}},
    ]

    return serialize_docs(list(coleccion.aggregate(pipeline)))
