"""
Panam — Dashboard Ejecutivo de Inteligencia de Negocio
=======================================================

Cumple la rúbrica del proyecto final:
  ✓ 4 KPIs / Highlights ejecutivos
  ✓ 5 gráficas (barras y líneas)
  ✓ 1 tabla resumen
  ✓ 3 variables (filtros) que reconfiguran las visualizaciones

Ejecutar:
    streamlit run dashboards/streamlit_dashboard.py

Requiere:
    pip install streamlit plotly pandas

Lee CSVs por defecto desde <repo>/data/. Si tienes Mongo/Cassandra arriba y
quieres consumir desde la API, cambia load_data() por llamadas a requests.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  Configuración global
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Panam — Dashboard Ejecutivo",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta corporativa (rojo Panam + complementarios)
PANAM_RED = "#E63946"
PANAM_DARK = "#1D3557"
PANAM_BLUE = "#457B9D"
PANAM_LIGHT = "#A8DADC"
PANAM_CREAM = "#F1FAEE"

PALETA = [PANAM_RED, PANAM_BLUE, PANAM_DARK, PANAM_LIGHT, "#F4A261", "#2A9D8F"]

# CSS para look ejecutivo
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #E63946 0%, #1D3557 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p  { color: #f8d7da; margin: 0.25rem 0 0 0; font-size: 1rem; }
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #E63946;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] { font-weight: 600; color: #1D3557; }
    [data-testid="stMetricValue"] { color: #E63946; font-size: 1.6rem; }
    .stPlotlyChart {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Carga de datos
# ─────────────────────────────────────────────────────────────────────────────
def get_data_dir() -> Path:
    """Sube hasta encontrar la carpeta data/ del repo."""
    here = Path(__file__).resolve()
    for p in [here.parent] + list(here.parents):
        if (p / "data").is_dir():
            return p / "data"
    raise FileNotFoundError("No se encontró carpeta data/")


@st.cache_data(show_spinner="Cargando datos de Panam…")
def load_data():
    d = get_data_dir()
    ventas = pd.read_csv(d / "ventas.csv", parse_dates=["fecha"])
    resenas = pd.read_csv(d / "resenas.csv", parse_dates=["fecha"])
    inv = pd.read_csv(d / "inventario.csv", parse_dates=["fecha"])
    ev = pd.read_csv(d / "eventos.csv", parse_dates=["fecha"])

    # Columnas derivadas que vamos a reutilizar
    ventas["ingreso"] = (
        ventas["cantidad"] * ventas["precio_unitario"] *
        (1 - ventas["descuento_pct"] / 100)
    ).round(2)
    ventas["estado"] = ventas["sucursal"].str.split("_").str[0]
    ventas["año_mes"] = ventas["fecha"].dt.to_period("M").dt.to_timestamp()
    ventas["año"] = ventas["fecha"].dt.year

    resenas["estado_modelo"] = resenas["modelo"].str.split().str[0]
    resenas["año_mes"] = resenas["fecha"].dt.to_period("M").dt.to_timestamp()

    return ventas, resenas, inv, ev


ventas, resenas, inv, eventos = load_data()

# ─────────────────────────────────────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>👟 Panam — Dashboard Ejecutivo</h1>
    <p>Inteligencia de Negocio NoSQL • Análisis de Retail en Tiempo Real</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar — 3 VARIABLES para reconfigurar gráficas (rúbrica 2.d)
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("### 🎛️ Filtros del Dashboard")
st.sidebar.markdown("*Ajusta las variables y mira cómo cambian las visualizaciones.*")

# Variable 1: rango de fechas
fecha_min = ventas["fecha"].min().date()
fecha_max = ventas["fecha"].max().date()
rango_fechas = st.sidebar.date_input(
    "📅 Periodo de análisis",
    value=(fecha_max - pd.Timedelta(days=365), fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
    help="Filtra ventas, reseñas y eventos por rango de fechas",
)

# Variable 2: estados/regiones (multiselect)
estados_disponibles = sorted(ventas["estado"].unique())
estados_sel = st.sidebar.multiselect(
    "🗺️ Estados",
    options=estados_disponibles,
    default=estados_disponibles,
    help="Filtra por uno o varios estados de la república",
)

# Variable 3: modelos (multiselect)
modelos_disponibles = sorted(ventas["modelo"].unique())
modelos_sel = st.sidebar.multiselect(
    "👟 Modelos",
    options=modelos_disponibles,
    default=modelos_disponibles,
    help="Foco en líneas específicas",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**📦 Volumen total:**  \n"
    f"{len(ventas):,} ventas  \n"
    f"{len(resenas):,} reseñas  \n"
    f"{len(inv):,} inventario  \n"
    f"{len(eventos):,} eventos"
)

# ─────────────────────────────────────────────────────────────────────────────
#  Aplicar filtros
# ─────────────────────────────────────────────────────────────────────────────
if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    f_ini, f_fin = pd.Timestamp(rango_fechas[0]), pd.Timestamp(rango_fechas[1])
else:
    f_ini, f_fin = ventas["fecha"].min(), ventas["fecha"].max()

mask_v = (
    (ventas["fecha"] >= f_ini) & (ventas["fecha"] <= f_fin) &
    (ventas["estado"].isin(estados_sel)) &
    (ventas["modelo"].isin(modelos_sel))
)
v = ventas[mask_v]

mask_r = (
    (resenas["fecha"] >= f_ini) & (resenas["fecha"] <= f_fin) &
    (resenas["modelo"].isin(modelos_sel))
)
r = resenas[mask_r]

if v.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Ajusta las variables.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  4 KPIs / Highlights (rúbrica 2.b)
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("📊 Indicadores Ejecutivos")

ingreso_total = v["ingreso"].sum()
unidades = int(v["cantidad"].sum())
ticket_prom = v["ingreso"].sum() / max(len(v), 1)
calif_prom = r["calificacion"].mean() if len(r) else 0.0

# Comparativa contra periodo previo del mismo tamaño
delta_dias = (f_fin - f_ini).days
prev_ini = f_ini - pd.Timedelta(days=delta_dias)
prev = ventas[
    (ventas["fecha"] >= prev_ini) & (ventas["fecha"] < f_ini) &
    (ventas["estado"].isin(estados_sel)) &
    (ventas["modelo"].isin(modelos_sel))
]
def _delta_pct(actual, anterior):
    if anterior == 0 or pd.isna(anterior):
        return None
    return (actual - anterior) / anterior * 100

d_ingreso = _delta_pct(ingreso_total, prev["ingreso"].sum())
d_unidades = _delta_pct(unidades, prev["cantidad"].sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "💰 Ingresos Totales",
    f"${ingreso_total/1_000_000:.2f}M",
    delta=f"{d_ingreso:+.1f}% vs periodo previo" if d_ingreso is not None else None,
)
k2.metric(
    "📦 Unidades Vendidas",
    f"{unidades:,}",
    delta=f"{d_unidades:+.1f}% vs periodo previo" if d_unidades is not None else None,
)
k3.metric(
    "🎫 Ticket Promedio",
    f"${ticket_prom:,.0f}",
)
k4.metric(
    "⭐ Calificación Promedio",
    f"{calif_prom:.2f}/5.0",
    delta=f"{(calif_prom - 3) * 20:+.0f}% sobre neutro" if calif_prom else None,
)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
#  5 GRÁFICAS (rúbrica 2.a)
# ─────────────────────────────────────────────────────────────────────────────

# ── Gráfica 1: línea — ingresos mensuales (TENDENCIA) ────────────────────
st.subheader("📈 1) Tendencia de Ingresos por Mes")
ingr_mes = v.groupby("año_mes", as_index=False)["ingreso"].sum()
fig1 = px.line(
    ingr_mes, x="año_mes", y="ingreso",
    markers=True,
    color_discrete_sequence=[PANAM_RED],
)
fig1.update_traces(line=dict(width=3), marker=dict(size=8))
fig1.update_layout(
    xaxis_title="Mes", yaxis_title="Ingresos (MXN)",
    hovermode="x unified", height=380, margin=dict(t=20, b=20),
    yaxis_tickformat=",.0f",
)
st.plotly_chart(fig1, use_container_width=True)

# ── Gráficas 2 y 3 lado a lado ───────────────────────────────────────────
c1, c2 = st.columns(2)

# Gráfica 2: barras — top modelos
with c1:
    st.subheader("🏆 2) Top Modelos por Ingresos")
    top_m = (
        v.groupby("modelo", as_index=False)["ingreso"].sum()
        .sort_values("ingreso", ascending=True).tail(10)
    )
    fig2 = px.bar(
        top_m, x="ingreso", y="modelo", orientation="h",
        color="ingreso", color_continuous_scale=[PANAM_LIGHT, PANAM_RED],
        text="ingreso",
    )
    fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig2.update_layout(
        xaxis_title="Ingresos (MXN)", yaxis_title="",
        height=420, showlegend=False, coloraxis_showscale=False,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

# Gráfica 3: barras apiladas — ventas por estado y método de pago
with c2:
    st.subheader("💳 3) Ventas por Estado y Método de Pago")
    by_estado = (
        v.groupby(["estado", "metodo_pago"], as_index=False)["cantidad"].sum()
    )
    fig3 = px.bar(
        by_estado, x="estado", y="cantidad", color="metodo_pago",
        color_discrete_sequence=PALETA, barmode="stack",
    )
    fig3.update_layout(
        xaxis_title="Estado", yaxis_title="Unidades",
        height=420, legend=dict(orientation="h", y=-0.25),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Gráficas 4 y 5 lado a lado ───────────────────────────────────────────
c3, c4 = st.columns(2)

# Gráfica 4: barras — distribución de tallas
with c3:
    st.subheader("👣 4) Distribución de Tallas Vendidas")
    by_talla = v.groupby("talla", as_index=False)["cantidad"].sum().sort_values("talla")
    by_talla["segmento"] = by_talla["talla"].apply(
        lambda t: "Infantil (12-21)" if t <= 21 else "Adulto (22-30)"
    )
    fig4 = px.bar(
        by_talla, x="talla", y="cantidad", color="segmento",
        color_discrete_map={
            "Infantil (12-21)": PANAM_BLUE,
            "Adulto (22-30)": PANAM_RED,
        },
    )
    fig4.update_layout(
        xaxis_title="Talla (mexicana)", yaxis_title="Unidades vendidas",
        height=420, legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig4, use_container_width=True)

# Gráfica 5: línea — sentimiento promedio mensual
with c4:
    st.subheader("💬 5) Evolución del Sentimiento del Cliente")
    if not r.empty:
        sent = r.groupby("año_mes", as_index=False)["calificacion"].mean()
        fig5 = px.line(
            sent, x="año_mes", y="calificacion",
            markers=True, color_discrete_sequence=[PANAM_DARK],
        )
        fig5.add_hline(y=3, line_dash="dash", line_color="gray",
                       annotation_text="Neutro (3.0)", annotation_position="right")
        fig5.update_traces(line=dict(width=3), marker=dict(size=7))
        fig5.update_layout(
            xaxis_title="Mes", yaxis_title="Calificación promedio",
            yaxis=dict(range=[1, 5]),
            height=420, margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Sin reseñas en el rango filtrado")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
#  TABLA RESUMEN (rúbrica 2.c)
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("📋 Tabla Resumen — Desempeño por Modelo")

tabla = (
    v.groupby("modelo")
    .agg(
        unidades=("cantidad", "sum"),
        ingresos=("ingreso", "sum"),
        precio_promedio=("precio_unitario", "mean"),
        ticket_promedio=("ingreso", "mean"),
        ventas_realizadas=("cantidad", "count"),
    )
    .round(2)
    .sort_values("ingresos", ascending=False)
    .reset_index()
)

# Adjuntar calificación promedio del modelo
calif_por_modelo = r.groupby("modelo")["calificacion"].mean().round(2)
tabla["calif_promedio"] = tabla["modelo"].map(calif_por_modelo).fillna(0)

# Adjuntar cantidad de reseñas
res_por_modelo = r.groupby("modelo").size()
tabla["n_resenas"] = tabla["modelo"].map(res_por_modelo).fillna(0).astype(int)

st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True,
    column_config={
        "modelo": st.column_config.TextColumn("👟 Modelo", width="medium"),
        "unidades": st.column_config.NumberColumn("📦 Unidades", format="%d"),
        "ingresos": st.column_config.NumberColumn("💰 Ingresos", format="$%.0f"),
        "precio_promedio": st.column_config.NumberColumn("💵 Precio prom.", format="$%.0f"),
        "ticket_promedio": st.column_config.NumberColumn("🎫 Ticket prom.", format="$%.0f"),
        "ventas_realizadas": st.column_config.NumberColumn("🔢 # Ventas", format="%d"),
        "calif_promedio": st.column_config.ProgressColumn(
            "⭐ Calificación", min_value=0, max_value=5, format="%.2f",
        ),
        "n_resenas": st.column_config.NumberColumn("💬 # Reseñas", format="%d"),
    },
)

# Footer
st.markdown("---")
st.caption(
    f"📊 Panam Dashboard v1.0 • Datos del {f_ini.date()} al {f_fin.date()} • "
    f"Mostrando {len(v):,} ventas filtradas de {len(ventas):,} totales"
)
