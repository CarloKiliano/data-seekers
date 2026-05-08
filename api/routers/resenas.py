"""
Endpoints de reseñas (MongoDB).

Expone la colección `resenas_enriquecidas` para que Power BI pueda graficar:
- Sentimiento promedio por modelo
- Reseñas por fuente (Instagram, TikTok, Twitter)
- Distribución de calificaciones
- Tendencia de sentimiento en el tiempo
"""

from fastapi import APIRouter, Query, HTTPException

from api.db.mongodb import MongoDB
from api.db.serializers import serialize_docs

router = APIRouter(prefix="/resenas", tags=["Reseñas (MongoDB)"])


@router.get(
    "",
    summary="Listar reseñas",
    description="Devuelve todas las reseñas, con filtros opcionales por modelo y sentimiento.",
)
def listar_resenas(
    modelo: str | None = Query(None, description="Filtrar por modelo (ej: '084')"),
    sentimiento: str | None = Query(
        None, description="Filtrar por sentimiento: 'positivo', 'negativo', 'neutro'"
    ),
    limite: int = Query(1000, ge=1, le=5000, description="Máximo de resultados"),
):
    """
    Obtiene reseñas. Power BI consume este endpoint como tabla principal.

    Ejemplo: GET /api/v1/resenas?modelo=084&sentimiento=positivo
    """
    coleccion = MongoDB.get_collection("resenas_enriquecidas")

    # Construir filtro dinámico solo con los parámetros enviados
    filtro = {}
    if modelo:
        filtro["modelo"] = modelo
    if sentimiento:
        filtro["sentimiento_calculado"] = sentimiento

    # Excluir _id de Mongo (no aporta y confunde a Power BI)
    cursor = coleccion.find(filtro, {"_id": 0}).limit(limite)
    documentos = list(cursor)

    return serialize_docs(documentos)


@router.get(
    "/por-modelo",
    summary="Sentimiento agregado por modelo",
    description="Para gráfica: 'Sentimiento promedio por modelo de calzado'.",
)
def resenas_por_modelo():
    """Agregación: cuenta reseñas y promedia sentimiento por modelo."""
    coleccion = MongoDB.get_collection("resenas_enriquecidas")

    pipeline = [
        {
            "$group": {
                "_id": "$modelo",
                "total_resenas": {"$sum": 1},
                "calificacion_promedio": {"$avg": "$calificacion"},
                "score_sentimiento_promedio": {"$avg": "$score_sentimiento"},
                "resenas_positivas": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$sentimiento_calculado", "positivo"]},
                            1,
                            0,
                        ]
                    }
                },
                "resenas_negativas": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$sentimiento_calculado", "negativo"]},
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {"$sort": {"total_resenas": -1}},
        {
            "$project": {
                "_id": 0,
                "modelo": "$_id",
                "total_resenas": 1,
                "calificacion_promedio": {"$round": ["$calificacion_promedio", 2]},
                "score_sentimiento_promedio": {
                    "$round": ["$score_sentimiento_promedio", 3]
                },
                "resenas_positivas": 1,
                "resenas_negativas": 1,
            }
        },
    ]

    resultados = list(coleccion.aggregate(pipeline))
    return serialize_docs(resultados)


@router.get(
    "/por-fuente",
    summary="Reseñas agregadas por fuente",
    description="Para gráfica: 'Volumen de reseñas por red social'.",
)
def resenas_por_fuente():
    """Agregación: cuenta reseñas por origen (Instagram, TikTok, etc.)."""
    coleccion = MongoDB.get_collection("resenas_enriquecidas")

    pipeline = [
        {
            "$group": {
                "_id": "$fuente",
                "total_resenas": {"$sum": 1},
                "score_sentimiento_promedio": {"$avg": "$score_sentimiento"},
                "likes_totales": {"$sum": "$likes"},
            }
        },
        {"$sort": {"total_resenas": -1}},
        {
            "$project": {
                "_id": 0,
                "fuente": "$_id",
                "total_resenas": 1,
                "score_sentimiento_promedio": {
                    "$round": ["$score_sentimiento_promedio", 3]
                },
                "likes_totales": 1,
            }
        },
    ]

    return serialize_docs(list(coleccion.aggregate(pipeline)))


@router.get(
    "/tendencia-sentimiento",
    summary="Tendencia de sentimiento por fecha",
    description="Para gráfica de líneas: 'Sentimiento a lo largo del tiempo'.",
)
def tendencia_sentimiento():
    """Agregación temporal: sentimiento promedio por día."""
    coleccion = MongoDB.get_collection("resenas_enriquecidas")

    pipeline = [
        {
            "$group": {
                "_id": "$fecha",
                "score_sentimiento_promedio": {"$avg": "$score_sentimiento"},
                "total_resenas": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "fecha": "$_id",
                "score_sentimiento_promedio": {
                    "$round": ["$score_sentimiento_promedio", 3]
                },
                "total_resenas": 1,
            }
        },
    ]

    return serialize_docs(list(coleccion.aggregate(pipeline)))
