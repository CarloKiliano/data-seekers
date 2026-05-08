"""
Endpoints de inventario (Cassandra).

Expone la tabla `inventario_por_almacen` para Power BI:
- Stock actual por almacén
- Alertas de stockout (stock bajo punto de reorden)
- Capacidad utilizada
"""

from collections import defaultdict
from fastapi import APIRouter, Query

from api.db.cassandra import CassandraDB
from api.db.serializers import serialize_docs

router = APIRouter(prefix="/inventario", tags=["Inventario (Cassandra)"])


@router.get(
    "",
    summary="Listar inventario",
    description="Devuelve el inventario con filtros opcionales.",
)
def listar_inventario(
    almacen: str | None = Query(None, description="Filtrar por almacén"),
    modelo: str | None = Query(None, description="Filtrar por modelo"),
    limite: int = Query(2000, ge=1, le=5000),
):
    """Inventario completo. Power BI lo usa como tabla principal de stock."""
    session = CassandraDB.get_session()
    rows = session.execute(f"SELECT * FROM inventario_por_almacen LIMIT {limite}").all()

    if almacen:
        rows = [r for r in rows if r.get("almacen") == almacen]
    if modelo:
        rows = [r for r in rows if r.get("modelo") == modelo]

    return serialize_docs(rows)


@router.get(
    "/alertas",
    summary="Alertas de stockout",
    description="Items donde stock <= punto de reorden. Para KPI ejecutivo.",
)
def alertas_stockout():
    """
    Filtra items con stock crítico (por debajo del punto de reorden).

    Power BI mostrará esto como una tabla roja en el dashboard.
    """
    session = CassandraDB.get_session()
    rows = session.execute("SELECT * FROM inventario_por_almacen").all()

    alertas = []
    for r in rows:
        stock = r.get("stock", 0) or 0
        punto_reorden = r.get("punto_reorden", 0) or 0

        if stock <= punto_reorden:
            alertas.append(
                {
                    "almacen": r.get("almacen"),
                    "modelo": r.get("modelo"),
                    "talla": r.get("talla"),
                    "stock_actual": stock,
                    "punto_reorden": punto_reorden,
                    "deficit": punto_reorden - stock,
                    "nivel_urgencia": (
                        "CRITICO"
                        if stock == 0
                        else "ALTO"
                        if stock < punto_reorden * 0.5
                        else "MEDIO"
                    ),
                }
            )

    alertas.sort(key=lambda x: x["deficit"], reverse=True)
    return alertas


@router.get(
    "/por-almacen",
    summary="Resumen de inventario por almacén",
    description="Para gráfica: 'Capacidad utilizada por almacén'.",
)
def inventario_por_almacen():
    """Agrega stock total y capacidad por almacén."""
    session = CassandraDB.get_session()
    rows = session.execute("SELECT * FROM inventario_por_almacen").all()

    agregado = defaultdict(
        lambda: {"stock_total": 0, "capacidad_total": 0, "n_items": 0}
    )

    for r in rows:
        alm = r.get("almacen")
        agregado[alm]["stock_total"] += r.get("stock", 0) or 0
        agregado[alm]["capacidad_total"] += r.get("capacidad_max", 0) or 0
        agregado[alm]["n_items"] += 1

    resultado = [
        {
            "almacen": alm,
            "stock_total": data["stock_total"],
            "capacidad_total": data["capacidad_total"],
            "n_items": data["n_items"],
            "ocupacion_pct": round(
                (data["stock_total"] / data["capacidad_total"] * 100), 2
            )
            if data["capacidad_total"] > 0
            else 0,
        }
        for alm, data in agregado.items()
    ]

    resultado.sort(key=lambda x: x["stock_total"], reverse=True)
    return resultado
