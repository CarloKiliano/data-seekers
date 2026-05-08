"""
Endpoint de KPIs ejecutivos.

Agrega métricas de MongoDB y Cassandra para el dashboard principal de Power BI.
Es el endpoint "estrella" para los 4 KPIs principales del proyecto.
"""

from fastapi import APIRouter

from api.db.mongodb import MongoDB
from api.db.cassandra import CassandraDB

router = APIRouter(prefix="/kpis", tags=["KPIs Ejecutivos"])


@router.get(
    "",
    summary="KPIs ejecutivos",
    description="Los 4 KPIs principales del dashboard: sentimiento, conversión, stock, ventas.",
)
def kpis_ejecutivos():
    """
    Devuelve los KPIs principales en un solo objeto.

    Power BI los muestra como tarjetas grandes (highlights) en el dashboard.
    """
    # ── KPI 1: Sentimiento promedio (MongoDB) ────────────────
    coleccion_resenas = MongoDB.get_collection("resenas_enriquecidas")
    pipeline_sentimiento = [
        {
            "$group": {
                "_id": None,
                "score_promedio": {"$avg": "$score_sentimiento"},
                "total_resenas": {"$sum": 1},
                "positivas": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$sentimiento_calculado", "positivo"]},
                            1,
                            0,
                        ]
                    }
                },
            }
        }
    ]
    resultado_sentimiento = list(coleccion_resenas.aggregate(pipeline_sentimiento))
    sentimiento = resultado_sentimiento[0] if resultado_sentimiento else {}

    # ── KPI 2: Tasa de conversión (MongoDB) ──────────────────
    coleccion_eventos = MongoDB.get_collection("eventos_web")
    vistas = coleccion_eventos.count_documents({"evento_tipo": "vista"})
    compras = coleccion_eventos.count_documents({"evento_tipo": "compra"})
    tasa_conversion = (compras / vistas * 100) if vistas > 0 else 0

    # ── KPI 3: Alertas de stock (Cassandra) ──────────────────
    session = CassandraDB.get_session()
    rows_inv = session.execute("SELECT stock, punto_reorden FROM inventario_por_almacen").all()
    items_alerta = sum(
        1
        for r in rows_inv
        if (r.get("stock") or 0) <= (r.get("punto_reorden") or 0)
    )
    total_items = len(rows_inv)

    # ── KPI 4: Ventas totales (Cassandra) ────────────────────
    rows_ventas = session.execute(
        "SELECT cantidad, precio_unitario, descuento_pct FROM ventas_por_sucursal"
    ).all()
    ingresos_totales = sum(
        (r.get("cantidad") or 0)
        * (r.get("precio_unitario") or 0)
        * (1 - (r.get("descuento_pct") or 0) / 100)
        for r in rows_ventas
    )
    unidades_totales = sum((r.get("cantidad") or 0) for r in rows_ventas)

    # ── Respuesta consolidada ─────────────────────────────────
    return {
        "sentimiento": {
            "score_promedio": round(sentimiento.get("score_promedio", 0) or 0, 3),
            "total_resenas": sentimiento.get("total_resenas", 0),
            "resenas_positivas": sentimiento.get("positivas", 0),
            "pct_positivas": round(
                (sentimiento.get("positivas", 0) / sentimiento.get("total_resenas", 1)) * 100,
                2,
            )
            if sentimiento.get("total_resenas", 0) > 0
            else 0,
        },
        "conversion": {
            "tasa_pct": round(tasa_conversion, 2),
            "total_vistas": vistas,
            "total_compras": compras,
        },
        "inventario": {
            "items_en_alerta": items_alerta,
            "total_items": total_items,
            "pct_alerta": round((items_alerta / total_items * 100), 2)
            if total_items > 0
            else 0,
        },
        "ventas": {
            "ingresos_totales": round(ingresos_totales, 2),
            "unidades_vendidas": unidades_totales,
            "n_transacciones": len(rows_ventas),
            "ticket_promedio": round(ingresos_totales / len(rows_ventas), 2)
            if len(rows_ventas) > 0
            else 0,
        },
    }
