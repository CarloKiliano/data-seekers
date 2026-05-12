# PANAM · Intelligence Hub

Dashboard ejecutivo custom en HTML/CSS/JS para el proyecto Data Seekers.

## 📁 Estructura

```
docs/
├── index.html                  # Estructura HTML
├── css/
│   └── styles.css              # Estilos (glassmorphism, gradients, animaciones)
├── js/
│   ├── utils.js                # Helpers de formato y mapeo de estados
│   ├── state.js                # Estado central + pub-sub
│   ├── filters.js              # Filtros (fecha, multiselect, reset)
│   ├── charts.js               # 5 gráficas con Chart.js
│   ├── map.js                  # Mapa coroplético de México con D3
│   ├── table.js                # Tabla con sort y click-filter
│   ├── kpis.js                 # Cálculo y render de KPIs
│   └── main.js                 # Orquestador
├── data/
│   ├── panam_data.json         # Datos del dashboard (generado)
│   └── mexico.json             # GeoJSON de México (descargar manualmente)
├── img/
│   └── panam_logo.png          # Logo opcional (cae a "P" gradient si no existe)
├── build_data.py               # Script para regenerar panam_data.json desde los CSVs
└── README.md
```

## 🚀 Cómo correr localmente

El dashboard usa `fetch()` para cargar los JSONs, por lo que **NO funciona con `file://`** (CORS). Necesitas un servidor HTTP simple.

```bash
cd docs/
python3 -m http.server 8000
# Abre http://localhost:8000 en tu navegador
```

O con Node:

```bash
npx serve docs/
```

## 🗺️ Setup del mapa (una sola vez)

Descarga el GeoJSON de México desde PhantomInsights:

```bash
mkdir -p docs/data
curl -L https://raw.githubusercontent.com/PhantomInsights/mexico-geojson/main/2022/mexico.json \
     -o docs/data/mexico.json
```

## 🔄 Regenerar datos del dashboard

Cuando actualices los CSVs con el script `scripts/generar_datos_masivos.py`:

```bash
# Desde la raíz del repo:
python docs/build_data.py
```

Esto lee `data/ventas.csv` y `data/resenas.csv`, samplea 5K + 2K registros con factor de escala, y genera `docs/data/panam_data.json` (~1 MB).

## 🌐 Publicar en GitHub Pages

1. Settings → Pages → Source: **Deploy from a branch**
2. Branch: `main`, folder: `/docs`
3. Save → en ~2 min el dashboard estará en:
   `https://<usuario>.github.io/<repo>/`

## 🎨 Features

- **3 filtros sincronizados**: rango de fechas + multiselect estados + multiselect modelos
- **4 KPIs ejecutivos** con gradient text y trends
- **5 gráficas interactivas** (Chart.js v4): tendencia, ranking, regional, tallas, sentimiento
- **Mapa coroplético de México** (D3 + GeoJSON real)
- **Tabla con sort y filtros**
- **Cross-filtering**: click cualquier elemento → filtra todo el dashboard
- **Glassmorphism + gradient mesh background**
- **Responsive** (mobile-friendly)

## 📦 Dependencias (CDN)

- [Chart.js 4.4.0](https://www.chartjs.org/)
- [D3.js 7.8.5](https://d3js.org/)
- Google Fonts: Bricolage Grotesque, Inter Tight, JetBrains Mono

## 🛠 Stack técnico

- **Vanilla JS** (sin framework), modular con patrón pub-sub
- **No build step** — abre el HTML directamente
- **No backend** — todos los datos viven en `data/panam_data.json`
- **No localStorage** — estado en memoria

## 📝 Notas

- El dashboard funciona contra un **sample de 5K ventas + 2K reseñas** con factor de escala (`scale_v` y `scale_r` en `meta`). Los totales se multiplican para reflejar el dataset completo.
- Si quieres mayor fidelidad por filtro: aumenta `--sample-ventas` y `--sample-resenas` en `build_data.py` (cuesta tamaño del JSON).
