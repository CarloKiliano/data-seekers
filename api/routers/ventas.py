"""
Endpoints de ventas (Cassandra).

Expone la tabla `ventas_por_sucursal` con agregaciones útiles:
- Ventas totales por sucursal
- Ventas por modelo
- Serie temporal de ventas

NOTA: Cassandra NO permite agregaciones complejas como SQL.
Las agregaciones se hacen en Python (en memoria) sobre los datos crudos.
Esto es aceptable para volúmenes pequeños/medianos como los del proyecto.
"""

from collections import defaultdict
from fastapi import APIRouter, Query

from api.db.cassandra import CassandraDB
from api.db.serializers import serialize_docs

router = APIRouter(prefix="/ventas", tags=["Ventas (Cassandra)"])


@router.get(
    "",
    summary="Listar ventas",
    description="Devuelve ventas con filtros opcionales por sucursal y modelo.",
)
def listar_ventas(
    sucursal: str | None = Query(None, description="Filtrar por sucursal"),
    modelo: str | None = Query(None, description="Filtrar por modelo"),
    limite: int = Query(2000, ge=1, le=5000),
):
    """
    Obtiene ventas. Power BI consume este endpoint como tabla principal de ventas.
    """
    session = CassandraDB.get_session()

    # En Cassandra los filtros se hacen con WHERE, pero requieren índices.
    # Para simplificar, traemos todo y filtramos en Python.
    query = f"SELECT * FROM ventas_por_sucursal LIMIT {limite}"
    rows = session.execute(query).all()

    # Filtros en Python
    if sucursal:
        rows = [r for r in rows if r.get("sucursal") == sucursal]
    if modelo:
        rows = [r for r in rows if r.get("modelo") == modelo]

    return serialize_docs(rows)


@router.get(
    "/por-sucursal",
    summary="Ventas agregadas por sucursal",
    description="Para gráfica: 'Ventas totales por sucursal'.",
)
def ventas_por_sucursal():
    """Agrega ventas por sucursal: total ingresos, unidades vendidas."""
    session = CassandraDB.get_session()
    rows = session.execute("SELECT * FROM ventas_por_sucursal").all()

    # Agregación en Python
    agregado = defaultdict(
        lambda: {"total_unidades": 0, "total_ingresos": 0.0, "n_transacciones": 0}
    )

    for r in rows:
        suc = r.get("sucursal")
        cantidad = r.get("cantidad", 0) or 0
        precio = r.get("precio_unitario", 0) or 0
        descuento = r.get("descuento_pct", 0) or 0

        ingreso = cantidad * precio * (1 - descuento / 100)

        agregado[suc]["total_unidades"] += cantidad
        agregado[suc]["total_ingresos"] += ingreso
        agregado[suc]["n_transacciones"] += 1

    resultado = [
        {
            "sucursal": suc,
            "total_unidades": data["total_unidades"],
            "total_ingresos": round(data["total_ingresos"], 2),
            "n_transacciones": data["n_transacciones"],
            "ticket_promedio": round(
                data["total_ingresos"] / data["n_transacciones"], 2
            )
            if data["n_transacciones"] > 0
            else 0,
        }
        for suc, data in agregado.items()
    ]

    resultado.sort(key=lambda x: x["total_ingresos"], reverse=True)
    return resultado


@router.get(
    "/por-modelo",
    summary="Ventas agregadas por modelo",
    description="Para gráfica: 'Modelos más vendidos'.",
)
def ventas_por_modelo():
    """Agrega ventas por modelo de calzado."""
    session = CassandraDB.get_session()
    rows = session.execute("SELECT * FROM ventas_por_sucursal").all()

    agregado = defaultdict(
        lambda: {"total_unidades": 0, "total_ingresos": 0.0, "n_transacciones": 0}
    )

    for r in rows:
        modelo = r.get("modelo")
        cantidad = r.get("cantidad", 0) or 0
        precio = r.get("precio_unitario", 0) or 0
        descuento = r.get("descuento_pct", 0) or 0

        ingreso = cantidad * precio * (1 - descuento / 100)

        agregado[modelo]["total_unidades"] += cantidad
        agregado[modelo]["total_ingresos"] += ingreso
        agregado[modelo]["n_transacciones"] += 1

    resultado = [
        {
            "modelo": modelo,
            "total_unidades": data["total_unidades"],
            "total_ingresos": round(data["total_ingresos"], 2),
            "n_transacciones": data["n_transacciones"],
        }
        for modelo, data in agregado.items()
    ]

    resultado.sort(key=lambda x: x["total_unidades"], reverse=True)
    return resultado


@router.get(
    "/por-fecha",
    summary="Serie temporal de ventas",
    description="Para gráfica de líneas: 'Tendencia de ventas en el tiempo'.",
)
def ventas_por_fecha():
    """Agrega ventas por fecha (serie temporal)."""
    session = CassandraDB.get_session()
    rows = session.execute("SELECT * FROM ventas_por_sucursal").all()

    agregado = defaultdict(
        lambda: {"total_unidades": 0, "total_ingresos": 0.0, "n_transacciones": 0}
    )

    for r in rows:
        fecha = r.get("fecha")
        # Convertir Date de Cassandra a string ISO
        fecha_str = fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha)

        cantidad = r.get("cantidad", 0) or 0
        precio = r.get("precio_unitario", 0) or 0
        descuento = r.get("descuento_pct", 0) or 0

        ingreso = cantidad * precio * (1 - descuento / 100)

        agregado[fecha_str]["total_unidades"] += cantidad
        agregado[fecha_str]["total_ingresos"] += ingreso
        agregado[fecha_str]["n_transacciones"] += 1

    resultado = [
        {
            "fecha": fecha,
            "total_unidades": data["total_unidades"],
            "total_ingresos": round(data["total_ingresos"], 2),
            "n_transacciones": data["n_transacciones"],
        }
        for fecha, data in agregado.items()
    ]

    resultado.sort(key=lambda x: x["fecha"])
    return resultado
