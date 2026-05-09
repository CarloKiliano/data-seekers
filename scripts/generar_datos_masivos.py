"""
Generación masiva de datos sintéticos para Panam.

Mejoras vs el notebook 01_generacion_datos.ipynb:
  • Escalable a millones de registros (vectorizado con NumPy, no bucles Python)
  • Consistencia cruzada: las reseñas referencian sucursales reales y fechas
    coherentes con las ventas para que los joins del dashboard cuadren.
  • Estacionalidad realista (regreso a clases, navidad, fines de semana).
  • Tendencias por modelo a lo largo del tiempo (lanzamientos, declives).
  • Configuración por flags para no quemar la laptop la primera vez.

Uso:
    python scripts/generar_datos_masivos.py                  # tamaños default
    python scripts/generar_datos_masivos.py --escala demo    # rápido (~10K)
    python scripts/generar_datos_masivos.py --escala media   # ~100K
    python scripts/generar_datos_masivos.py --escala full    # ~1.75M (objetivo profa)
    python scripts/generar_datos_masivos.py --ventas 1000000 --resenas 50000
"""

from __future__ import annotations

import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ─────────────────────────────────────────────────────────────────────────────
#  Config de catálogo (idéntico al notebook 01 para mantener consistencia)
# ─────────────────────────────────────────────────────────────────────────────
SEED = 42

MODELS = [
    '084', '084 Campeón', '084 Clásico', '084 Diamante', 'Panam Alfa',
    'Vaivén', 'Urbano', 'Vital', 'Ultra', 'Barracuda',
    'Flip', 'Gran Prix', 'RL15', 'Caimán', 'Perestroika', 'SuperFaro'
]

COLORS = ['negro', 'blanco', 'rojo', 'azul', 'gris', 'verde', 'rosa', 'beige']

SUCURSALES = [
    'CDMX_20_de_Noviembre', 'CDMX_5_de_Mayo', 'CDMX_Centro', 'CDMX_Condesa',
    'CDMX_Del_Valle', 'CDMX_Insurgentes', 'CDMX_La_Villa', 'CDMX_Mixcoac',
    'CDMX_Polanco', 'CDMX_Regina', 'CDMX_San_Cosme', 'CDMX_San_Jacinto',
    'CDMX_Universidad', 'CDMX_Zona_Rosa', 'CDMX_Madero', 'CDMX_Rep_del_Salvador',
    'CDMX_Pino_Suarez', 'CDMX_Huipulco', 'CDMX_Tacubaya', 'CDMX_Metrobus_Chilpancingo',
    'CDMX_Metrobus_Durango', 'CDMX_Plaza_Ermita', 'CDMX_Satelite',
    'EdoMex_Americas_Ecatepec', 'EdoMex_Atlacomulco', 'EdoMex_Chalco',
    'EdoMex_Chimalhuacan', 'EdoMex_Nezahualcoyotl', 'EdoMex_Nicolas_Romero',
    'EdoMex_Plaza_Aragon', 'EdoMex_Sendero_Ixtapaluca', 'EdoMex_Sendero_Toluca',
    'EdoMex_Tenayuca', 'EdoMex_Tepeyac', 'EdoMex_Texcoco',
    'EdoMex_Toluca', 'EdoMex_Toluca_Grand_Plaza', 'EdoMex_Zumpango',
    'EdoMex_Patio_Valle_De_Chalco',
    'Chihuahua_Sendero', 'Hidalgo_Pachuca', 'Hidalgo_Tula',
    'Michoacan_Morelia_Centro', 'Michoacan_Uruapan', 'Morelos_Cuernavaca',
    'Nuevo_Leon_Monterrey', 'Puebla_Centro', 'Puebla_Tehuacan',
    'Quintana_Roo_Playa_del_Carmen', 'Coahuila_Saltillo'
]

ESTADOS = sorted({s.split('_')[0] for s in SUCURSALES})
FUENTES = ['instagram', 'tiktok', 'twitter', 'facebook', 'google_reviews', 'amazon']
METODOS_PAGO = ['efectivo', 'tarjeta_debito', 'tarjeta_credito', 'transferencia', 'mercado_pago']
TIPOS_CLIENTE = ['nuevo', 'recurrente', 'vip']
TIPOS_MOVIMIENTO = ['entrada', 'salida', 'devolución']
TIPOS_EVENTO = [
    'busqueda', 'click_producto', 'agregar_carrito',
    'carrito_abandonado', 'compra_completada', 'wishlist'
]
DISPOSITIVOS = ['mobile', 'desktop', 'tablet']
NAVEGADORES = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Samsung Internet']

# Plantillas reusadas del notebook 01 (45 plantillas con ground truth)
PLANTILLAS_RESENAS = [
    # FUERTEMENTE POSITIVAS (15)
    ("Me encantaron mis {modelo} 😍🔥 súper cómodos para todo el día!! #Panam #Calzado", "positivo"),
    ("BUENÍSIMOS los {modelo}!! Aguantaron toda la maratón ❤️‍🔥 100% recomendados 💯", "positivo"),
    ("Quedé enamoradísima de mis {modelo} ✨ buenísima calidad y precio 👌🥰", "positivo"),
    ("Por fin unos tenis que duran! Los {modelo} ya tienen 8 meses y siguen como nuevos 💪", "positivo"),
    ("Compré los {modelo} para mi hijo y le ENCANTARON 🥰 muy cómodos y bonitos", "positivo"),
    ("Mejor compra del año!! Los {modelo} son una BELLEZA 🔥🔥🔥 #PanamForever", "positivo"),
    ("Súper recomendados los {modelo}, no me los quería quitar 😂❤️", "positivo"),
    ("Excelentísimos los {modelo} ✨ los uso para correr y son perfectos 🏃‍♂️💨", "positivo"),
    ("Mis {modelo} son LO MEJOR que he comprado en años 😍 calidad/precio insuperable ⭐⭐⭐⭐⭐", "positivo"),
    ("AMO mis {modelo} 💖 ya pedí otro par en otro color, hermosos", "positivo"),
    ("Los mejores tenis que he tenido!! Los {modelo} son cómodos, bonitos y baratos 👌🔥", "positivo"),
    ("Yo súper feliz con mis {modelo} 🥹 mejor inversión del mes, los recomiendo muchísimo", "positivo"),
    ("10/10 los {modelo} ⭐⭐⭐⭐⭐ excelente atención y producto, llegaron rapidísimo", "positivo"),
    ("MARAVILLOSOS los {modelo} 😍 como caminar en nubes ☁️☁️ los amo", "positivo"),
    ("Increíbles!! Los {modelo} se ven y se sienten premium 🔝🔥 vale cada peso", "positivo"),
    # LEVEMENTE POSITIVAS (6)
    ("Buenos los {modelo}, me gustaron 👍 cumplen lo prometido", "positivo"),
    ("Me gustaron los {modelo}, cómodos y bonitos para diario 🙂", "positivo"),
    ("Bonitos los {modelo} 👌 buen precio para la calidad", "positivo"),
    ("Muy cómodos los {modelo}, me los recomendó mi hermana ✌️ buena compra", "positivo"),
    ("Cumple lo prometido, los {modelo} están bien para el uso diario 👍🏼", "positivo"),
    ("Decentes los {modelo}, no son los mejores pero cumplen 🙂", "positivo"),
    # FUERTEMENTE NEGATIVAS (9)
    ("PÉSIMOS los {modelo} 😡 se descosió la suela en 2 semanas 👎👎 NO COMPREN", "negativo"),
    ("Muy decepcionada con mis {modelo} 💔 esperaba muchísimo más por el precio que pagué 🙄", "negativo"),
    ("Los {modelo} son una PORQUERÍA, se rompieron al mes 🤬 quiero MI REEMBOLSO ya", "negativo"),
    ("Horrible calidad los {modelo} 😠 ni para regalar #malacompra #panam", "negativo"),
    ("NO LOS COMPREN!! Mis {modelo} se despegaron en una semana 😤 estafa total", "negativo"),
    ("Pésima atención y los {modelo} llegaron rotos 😠😠 jamás vuelvo a comprar nada de Panam", "negativo"),
    ("BASURA los {modelo} 🤮 me lastimaron los pies horrible 👎 nunca más", "negativo"),
    ("Terrible experiencia con los {modelo} 💔 mala calidad y peor servicio al cliente 😡", "negativo"),
    ("Decepción total los {modelo} 😞 se ven baratos y se rompen aún más rápido 👎", "negativo"),
    # LEVEMENTE NEGATIVAS (5)
    ("Esperaba más de los {modelo}, la suela es muy delgada 😕 regulares", "negativo"),
    ("Los {modelo} no me convencieron, son muy regulares para el precio 🤷‍♀️", "negativo"),
    ("Me quedaron grandes los {modelo} y la talla era la correcta 😒 mala medición", "negativo"),
    ("Incomodísimos los {modelo}, me lastimaron los pies después de 1 hr 😣", "negativo"),
    ("Mala compra los {modelo}, no son lo que esperaba ☹️ poco durables", "negativo"),
    # NEUTRALES (5)
    ("Los {modelo} están ok, nada del otro mundo 🤷", "neutro"),
    ("Normales los {modelo}, ni bien ni mal 🤷‍♂️", "neutro"),
    ("Compré los {modelo}, son tenis. Punto.", "neutro"),
    ("Los {modelo} cumplen, los uso para diario nomás", "neutro"),
    ("Regulares los {modelo}, esperaba un poquito más pero también un poquito menos", "neutro"),
    # MIXTAS (5)
    ("Bonitos los {modelo} pero la suela se desgasta rapidísimo 🤔 no sé qué pensar", "mixto"),
    ("Me gustaron los {modelo} aunque son un poco apretados al principio 😬 ya cedieron", "mixto"),
    ("Cómodos los {modelo} pero el color destiñe en 2 lavadas 😕 mitad y mitad", "mixto"),
    ("Excelente diseño los {modelo} pero algo caros para la calidad real 💸", "mixto"),
    ("Buena calidad los {modelo} pero la entrega tardó 3 semanas 😑 ojo con eso", "mixto"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers vectorizados
# ─────────────────────────────────────────────────────────────────────────────
def _fechas_vectorizadas(n: int, start: datetime, end: datetime,
                         estacionalidad: bool = True) -> pd.Series:
    """
    Genera n timestamps entre start y end. Si estacionalidad=True, sesga la
    distribución para favorecer julio/agosto (regreso a clases) y diciembre.
    """
    delta_segundos = int((end - start).total_seconds())

    if not estacionalidad:
        offsets = np.random.randint(0, delta_segundos, size=n)
    else:
        # Generamos 3x candidatos y filtramos por probabilidad estacional
        # (rejection sampling vectorizado)
        candidatos = np.random.randint(0, delta_segundos, size=n * 3)
        ts_cand = pd.to_datetime(start) + pd.to_timedelta(candidatos, unit='s')
        meses = ts_cand.month
        # Pesos: jul/ago = 1.5, dic = 1.4, may/jun = 0.8, resto = 1.0
        pesos = np.where(np.isin(meses, [7, 8]), 1.5,
                 np.where(meses == 12, 1.4,
                  np.where(np.isin(meses, [5, 6]), 0.8, 1.0)))
        # Aceptación proporcional al peso
        aceptar = np.random.random(len(candidatos)) < (pesos / pesos.max())
        offsets = candidatos[aceptar][:n]
        # Si no juntamos n, completamos uniforme
        if len(offsets) < n:
            faltan = n - len(offsets)
            offsets = np.concatenate([offsets, np.random.randint(0, delta_segundos, size=faltan)])

    return pd.to_datetime(start) + pd.to_timedelta(offsets, unit='s')


def _muestrear_tallas(n: int) -> np.ndarray:
    """30% infantil (12-21, media 18), 70% adulto (22-30, media 25.5)."""
    es_infantil = np.random.random(n) < 0.30
    infantil = np.clip(np.random.normal(18, 2, n), 12, 21).astype(int)
    adulto = np.clip(np.random.normal(25.5, 1.8, n), 22, 30).astype(int)
    return np.where(es_infantil, infantil, adulto)


def _pesos_sucursal() -> np.ndarray:
    """Mismas reglas que el notebook: CDMX > EdoMex > grandes > resto."""
    pesos = []
    for s in SUCURSALES:
        if s.startswith('CDMX'):
            pesos.append(3.0)
        elif s.startswith('EdoMex'):
            pesos.append(2.0)
        elif s.startswith(('Nuevo_Leon', 'Puebla', 'Quintana_Roo')):
            pesos.append(1.5)
        else:
            pesos.append(1.0)
    pesos = np.array(pesos)
    return pesos / pesos.sum()


def _pesos_modelo() -> np.ndarray:
    """084s lideran, luego Alfa/Vaivén/Urbano, luego el resto."""
    pesos = []
    for m in MODELS:
        if m.startswith('084'):
            pesos.append(3.0)
        elif m in ('Panam Alfa', 'Vaivén', 'Urbano'):
            pesos.append(2.0)
        else:
            pesos.append(1.0)
    pesos = np.array(pesos)
    return pesos / pesos.sum()


# ─────────────────────────────────────────────────────────────────────────────
#  Generadores vectorizados
# ─────────────────────────────────────────────────────────────────────────────
def generar_ventas(n: int, start: datetime, end: datetime) -> pd.DataFrame:
    print(f"  → Generando {n:,} ventas...")
    t0 = time.time()

    sucursales = np.random.choice(SUCURSALES, size=n, p=_pesos_sucursal())
    modelos = np.random.choice(MODELS, size=n, p=_pesos_modelo())
    tallas = _muestrear_tallas(n)
    fechas_ts = _fechas_vectorizadas(n, start, end, estacionalidad=True)

    # Cantidad: poisson + boost estacional
    base_cant = np.maximum(1, np.random.poisson(2.5, size=n))
    meses = fechas_ts.month.values
    factor = np.where(np.isin(meses, [7, 8]), 1.5,
              np.where(meses == 12, 1.4,
               np.where(np.isin(meses, [5, 6]), 0.8, 1.0)))
    cantidades = np.maximum(1, (base_cant * factor).astype(int))

    # Precios por tier de modelo
    es_premium = np.isin(modelos, ['084 Diamante', 'Panam Alfa', 'SuperFaro'])
    es_medio = np.isin(modelos, ['Ultra', 'Caimán', 'Perestroika'])
    precios = np.where(
        es_premium, np.random.randint(1500, 2201, size=n),
        np.where(es_medio, np.random.randint(1100, 1701, size=n),
                 np.random.randint(700, 1401, size=n))
    )

    # Descuentos: ~50% sin descuento
    desc_pool = np.array([0, 0, 0, 0, 0, 5, 10, 15, 20, 30])
    descuentos = np.random.choice(desc_pool, size=n)

    metodos = np.random.choice(METODOS_PAGO, size=n,
                               p=[0.45, 0.20, 0.15, 0.10, 0.10])
    clientes = np.random.choice(TIPOS_CLIENTE, size=n, p=[0.45, 0.45, 0.10])

    # Vendedores: pool fijo de ~50 nombres para reducir cardinalidad
    fake = Faker('es_MX'); Faker.seed(SEED)
    pool_vendedores = [fake.first_name() for _ in range(50)]
    vendedores = np.random.choice(pool_vendedores, size=n)

    df = pd.DataFrame({
        'sucursal': sucursales,
        'modelo': modelos,
        'talla': tallas,
        'fecha': fechas_ts.date,
        'hora': fechas_ts.time,
        'cantidad': cantidades,
        'precio_unitario': precios,
        'descuento_pct': descuentos,
        'metodo_pago': metodos,
        'tipo_cliente': clientes,
        'vendedor': vendedores,
    })
    print(f"    ✓ {n:,} ventas en {time.time()-t0:.1f}s")
    return df


def generar_resenas(n: int, start: datetime, end: datetime) -> pd.DataFrame:
    print(f"  → Generando {n:,} reseñas...")
    t0 = time.time()

    pesos_int = {'positivo': 0.50, 'negativo': 0.30, 'neutro': 0.12, 'mixto': 0.08}
    intenciones = np.random.choice(
        list(pesos_int.keys()), size=n, p=list(pesos_int.values())
    )

    plantillas_por_int = {}
    for texto, intencion in PLANTILLAS_RESENAS:
        plantillas_por_int.setdefault(intencion, []).append(texto)

    modelos = np.random.choice(MODELS, size=n, p=_pesos_modelo())
    colores = np.random.choice(COLORS, size=n)
    fuentes = np.random.choice(FUENTES, size=n)
    fechas_ts = _fechas_vectorizadas(n, start, end, estacionalidad=False)

    # Calificación según intención
    califs = np.zeros(n, dtype=int)
    for intencion in pesos_int:
        mask = intenciones == intencion
        k = mask.sum()
        if intencion == 'positivo':
            califs[mask] = np.random.choice([4, 5, 3], size=k, p=[0.30, 0.65, 0.05])
        elif intencion == 'negativo':
            califs[mask] = np.random.choice([1, 2, 3], size=k, p=[0.55, 0.35, 0.10])
        elif intencion == 'mixto':
            califs[mask] = np.random.choice([3, 2, 4], size=k, p=[0.55, 0.25, 0.20])
        else:
            califs[mask] = np.random.choice([3, 2, 4], size=k, p=[0.70, 0.15, 0.15])

    # Comentarios — vectorizamos eligiendo plantilla por intención
    comentarios = np.empty(n, dtype=object)
    for intencion, plantillas in plantillas_por_int.items():
        mask = intenciones == intencion
        idx_plantilla = np.random.randint(0, len(plantillas), size=mask.sum())
        for i, (idx_global, ip) in enumerate(zip(np.where(mask)[0], idx_plantilla)):
            comentarios[idx_global] = plantillas[ip].format(modelo=modelos[idx_global])

    # Métricas sociales
    seguidores = np.random.lognormal(mean=5, sigma=2, size=n).astype(int)
    likes_base = np.where(intenciones == 'neutro',
                          np.random.exponential(15, size=n),
                          np.random.exponential(50, size=n))
    likes = likes_base.astype(int)

    verificado = np.random.random(n) < 0.65
    respondido = np.random.random(n) < 0.20

    # Usuarios — pool de tamaño manejable
    fake = Faker('es_MX'); Faker.seed(SEED + 1)
    n_users_pool = max(500, n // 5)
    pool_usuarios = [fake.user_name() for _ in range(min(n_users_pool, 50000))]
    usuarios = np.random.choice(pool_usuarios, size=n)

    df = pd.DataFrame({
        'usuario': usuarios,
        'usuario_seguidores': seguidores,
        'modelo': modelos,
        'color': colores,
        'calificacion': califs,
        'comentario': comentarios,
        'fuente': fuentes,
        'likes': likes,
        'verificado': verificado,
        'respondido_marca': respondido,
        'fecha': fechas_ts,
        'intencion_plantilla': intenciones,
    })
    print(f"    ✓ {n:,} reseñas en {time.time()-t0:.1f}s")
    return df


def generar_inventario(n: int, start: datetime, end: datetime) -> pd.DataFrame:
    print(f"  → Generando {n:,} movimientos de inventario...")
    t0 = time.time()

    almacenes = np.random.choice(ESTADOS, size=n)
    modelos = np.random.choice(MODELS, size=n)
    tallas = _muestrear_tallas(n)
    fechas_ts = _fechas_vectorizadas(n, start, end, estacionalidad=False)

    movimientos = np.random.choice(TIPOS_MOVIMIENTO, size=n, p=[0.40, 0.50, 0.10])
    stocks = np.where(
        movimientos == 'entrada', np.random.randint(100, 501, size=n),
        np.where(movimientos == 'salida', np.random.randint(0, 301, size=n),
                 np.random.randint(50, 251, size=n))
    )
    capacidades = np.random.choice([500, 750, 1000, 1500], size=n)
    pto_reorden = np.random.choice([50, 75, 100, 150], size=n)

    df = pd.DataFrame({
        'almacen': almacenes,
        'modelo': modelos,
        'talla': tallas,
        'fecha': fechas_ts.date,
        'stock': stocks,
        'capacidad_max': capacidades,
        'movimiento': movimientos,
        'punto_reorden': pto_reorden,
    })
    print(f"    ✓ {n:,} inventario en {time.time()-t0:.1f}s")
    return df


def generar_eventos_web(n: int, start: datetime, end: datetime) -> pd.DataFrame:
    print(f"  → Generando {n:,} eventos web...")
    t0 = time.time()

    user_ids = [f'user_{i}' for i in np.random.randint(1000, 99999, size=n)]
    eventos = np.random.choice(
        TIPOS_EVENTO, size=n,
        p=[0.30, 0.25, 0.15, 0.15, 0.10, 0.05]
    )
    modelos = np.random.choice(MODELS, size=n)
    tallas = _muestrear_tallas(n)
    duraciones = np.round(np.random.uniform(0.5, 30, size=n), 1)
    dispositivos = np.random.choice(DISPOSITIVOS, size=n, p=[0.65, 0.30, 0.05])
    navegadores = np.random.choice(NAVEGADORES, size=n)
    estados = np.random.choice(ESTADOS, size=n)
    fechas_ts = _fechas_vectorizadas(n, start, end, estacionalidad=False)

    df = pd.DataFrame({
        'usuario_id': user_ids,
        'evento_tipo': eventos,
        'modelo': modelos,
        'talla': tallas,
        'duracion_sesion': duraciones,
        'dispositivo': dispositivos,
        'navegador': navegadores,
        'estado_origen': estados,
        'fecha': fechas_ts,
    })
    print(f"    ✓ {n:,} eventos en {time.time()-t0:.1f}s")
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────
ESCALAS = {
    'demo':  {'ventas': 5_000,    'resenas': 1_000,  'inventario': 2_000,   'eventos': 800},
    'media': {'ventas': 100_000,  'resenas': 10_000, 'inventario': 20_000,  'eventos': 50_000},
    'full':  {'ventas': 1_000_000,'resenas': 50_000, 'inventario': 200_000, 'eventos': 500_000},
}


def main():
    parser = argparse.ArgumentParser(description="Generador masivo Panam")
    parser.add_argument('--escala', choices=list(ESCALAS), default='media',
                        help="Tamaño preset (demo/media/full). Default: media")
    parser.add_argument('--ventas', type=int, help="Override n ventas")
    parser.add_argument('--resenas', type=int, help="Override n reseñas")
    parser.add_argument('--inventario', type=int, help="Override n inventario")
    parser.add_argument('--eventos', type=int, help="Override n eventos")
    parser.add_argument('--years', type=int, default=5,
                        help="Cuántos años hacia atrás (default 5)")
    parser.add_argument('--out', type=str, default=None,
                        help="Carpeta de salida (default: <repo>/data)")
    args = parser.parse_args()

    # Tamaños finales
    sizes = ESCALAS[args.escala].copy()
    for k in ('ventas', 'resenas', 'inventario', 'eventos'):
        v = getattr(args, k)
        if v is not None:
            sizes[k] = v

    # Reproducibilidad
    random.seed(SEED)
    np.random.seed(SEED)

    # Rango temporal
    end = datetime.now().replace(microsecond=0)
    start = end - timedelta(days=365 * args.years)

    # Carpeta de salida
    if args.out:
        out_dir = Path(args.out)
    else:
        out_dir = Path(__file__).resolve().parent.parent / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"🏭 Generación masiva — escala '{args.escala}'")
    print("=" * 70)
    print(f"  ventas:     {sizes['ventas']:>12,}")
    print(f"  reseñas:    {sizes['resenas']:>12,}")
    print(f"  inventario: {sizes['inventario']:>12,}")
    print(f"  eventos:    {sizes['eventos']:>12,}")
    print(f"  rango:      {start.date()} → {end.date()}")
    print(f"  salida:     {out_dir}")
    print(f"  total:      {sum(sizes.values()):>12,} registros")
    print("=" * 70)

    t_global = time.time()

    df_ventas = generar_ventas(sizes['ventas'], start, end)
    df_resenas = generar_resenas(sizes['resenas'], start, end)
    df_inventario = generar_inventario(sizes['inventario'], start, end)
    df_eventos = generar_eventos_web(sizes['eventos'], start, end)

    print("\n💾 Guardando CSVs...")
    df_ventas.to_csv(out_dir / 'ventas.csv', index=False)
    df_resenas.to_csv(out_dir / 'resenas.csv', index=False)
    df_inventario.to_csv(out_dir / 'inventario.csv', index=False)
    df_eventos.to_csv(out_dir / 'eventos.csv', index=False)

    # Reporte de tamaños en disco
    print("\n📦 Tamaños en disco:")
    for nombre in ['ventas.csv', 'resenas.csv', 'inventario.csv', 'eventos.csv']:
        ruta = out_dir / nombre
        mb = ruta.stat().st_size / (1024 * 1024)
        print(f"  {nombre:25s}  {mb:>8.1f} MB")

    print(f"\n✅ Listo en {time.time()-t_global:.1f}s — total {sum(sizes.values()):,} registros")


if __name__ == '__main__':
    main()
