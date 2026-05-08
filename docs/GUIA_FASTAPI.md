# 🚀 Guía Completa: API REST con FastAPI

> Esta guía te explica qué es FastAPI, cómo funciona la API que construimos,
> y cómo usarla. Pensada para alguien que parte de cero.

---

## 📑 Tabla de Contenidos

1. [¿Qué es FastAPI y por qué lo usamos?](#qué-es-fastapi)
2. [Arquitectura del API](#arquitectura)
3. [Instalación y Primer Arranque](#instalación)
4. [Endpoints Disponibles](#endpoints)
5. [Cómo Funciona Cada Pieza](#cómo-funciona)
6. [Probar la API](#probar)
7. [Conceptos Clave de FastAPI](#conceptos)

---

<a name="qué-es-fastapi"></a>
## 1️⃣ ¿Qué es FastAPI y por qué lo usamos?

**FastAPI** es un framework de Python para construir APIs REST. En palabras simples: te permite crear "endpoints" (URLs) que devuelven datos en JSON cuando alguien hace una petición HTTP.

### ¿Por qué FastAPI y no Flask o Django?

| Característica | FastAPI | Flask | Django |
|---|---|---|---|
| Velocidad | 🚀 Muy rápida | 🐢 Media | 🐢 Media |
| Documentación auto | ✅ Sí (Swagger) | ❌ No | ❌ No |
| Validación de datos | ✅ Automática | ❌ Manual | ⚠️ Compleja |
| Curva de aprendizaje | 📈 Suave | 📈 Suave | 📉 Empinada |
| Type hints | ✅ Nativo | ⚠️ Opcional | ❌ Limitado |

### ¿Qué hace nuestra API?

```
                    ┌─────────────────────────┐
                    │      Power BI / Cliente  │
                    └────────────┬────────────┘
                                 │ HTTP GET
                                 │ "tráeme las ventas"
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI (Python)   │
                    │   ┌──────────────────┐  │
                    │   │   Routers        │  │
                    │   │   - resenas      │  │
                    │   │   - ventas       │  │
                    │   │   - inventario   │  │
                    │   │   - kpis         │  │
                    │   └──────────────────┘  │
                    └────────┬────────────────┘
                             │ Query
                             ▼
            ┌────────────────┴────────────────┐
            │                                  │
    ┌───────▼─────────┐              ┌────────▼─────────┐
    │    MongoDB      │              │    Cassandra     │
    │  - resenas      │              │  - ventas        │
    │  - eventos_web  │              │  - inventario    │
    └─────────────────┘              └──────────────────┘
```

**Flujo:** Power BI → HTTP request → FastAPI → MongoDB/Cassandra → datos JSON → Power BI

---

<a name="arquitectura"></a>
## 2️⃣ Arquitectura del API

Estructuramos el código siguiendo el patrón **modular por dominio** (best practice profesional):

```
api/
├── __init__.py              ← Marca la carpeta como paquete Python
├── main.py                  ← Punto de entrada: crea la app FastAPI
├── config.py                ← Lee variables de .env (URIs de BDs, puertos)
├── db/
│   ├── __init__.py
│   ├── mongodb.py           ← Cliente de MongoDB (singleton)
│   ├── cassandra.py         ← Cliente de Cassandra (singleton)
│   └── serializers.py       ← Convierte tipos de BD a JSON
└── routers/
    ├── __init__.py
    ├── resenas.py           ← Endpoints /api/v1/resenas/*
    ├── eventos.py           ← Endpoints /api/v1/eventos/*
    ├── ventas.py            ← Endpoints /api/v1/ventas/*
    ├── inventario.py        ← Endpoints /api/v1/inventario/*
    └── kpis.py              ← Endpoints /api/v1/kpis
```

### ¿Por qué esta estructura?

- **Separación de responsabilidades**: cada archivo tiene un único propósito.
- **Escalable**: agregar un nuevo dominio = agregar un nuevo router (sin tocar lo existente).
- **Testeable**: puedes hacer tests por separado de cada router.
- **Profesional**: así trabajan empresas que usan FastAPI en producción.

---

<a name="instalación"></a>
## 3️⃣ Instalación y Primer Arranque

### Paso 1 — Actualizar dependencias

El nuevo `requirements.txt` ya incluye FastAPI. Si ya hiciste el setup, solo reinstala:

```bash
# Activa tu entorno virtual primero
source .venv/bin/activate           # macOS/Linux
# .venv\Scripts\activate            # Windows

pip install -r requirements.txt
```

### Paso 2 — Asegúrate de que las BDs estén corriendo

```bash
docker-compose up -d mongodb cassandra
```

Espera ~30s a que Cassandra termine de iniciar.

### Paso 3 — Arrancar la API

Tienes **dos formas** de hacerlo:

**Opción A — Más simple (recomendada):**
```bash
python run_api.py
```

**Opción B — Con uvicorn directamente (más control):**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

> **¿Qué hace `--reload`?** Cuando edites cualquier archivo `.py`, la API se reinicia automáticamente. Solo úsalo en desarrollo, NUNCA en producción.

### Paso 4 — Verificar que funciona

Abre en tu navegador:

🌐 **http://localhost:8000** → Info básica del API
🌐 **http://localhost:8000/docs** → Documentación interactiva (Swagger UI)
🌐 **http://localhost:8000/health** → Verifica que las BDs respondan

Si todo está bien, verás algo como:

```json
{
  "app": "Panam NoSQL API",
  "version": "1.0.0",
  "status": "ok",
  "docs": "/docs",
  "endpoints_principales": [
    "/api/v1/resenas",
    "/api/v1/eventos",
    "/api/v1/ventas",
    "/api/v1/inventario",
    "/api/v1/kpis"
  ]
}
```

---

<a name="endpoints"></a>
## 4️⃣ Endpoints Disponibles

Todos los endpoints empiezan con `/api/v1/...`

### 📝 Reseñas (MongoDB)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/resenas` | Lista de reseñas (con filtros opcionales) |
| GET | `/api/v1/resenas/por-modelo` | Sentimiento agregado por modelo |
| GET | `/api/v1/resenas/por-fuente` | Reseñas por red social |
| GET | `/api/v1/resenas/tendencia-sentimiento` | Sentimiento por fecha (serie temporal) |

**Filtros disponibles** en `/api/v1/resenas`:
- `?modelo=084` — filtra por modelo específico
- `?sentimiento=positivo` — filtra por sentimiento
- `?limite=500` — máximo de resultados (default 1000)

### 🌐 Eventos Web (MongoDB)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/eventos` | Lista de eventos web |
| GET | `/api/v1/eventos/conversion` | Tasa de conversión por modelo |
| GET | `/api/v1/eventos/por-dispositivo` | Eventos por dispositivo + tipo |

### 💰 Ventas (Cassandra)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/ventas` | Lista de ventas |
| GET | `/api/v1/ventas/por-sucursal` | Ventas agregadas por sucursal |
| GET | `/api/v1/ventas/por-modelo` | Modelos más vendidos |
| GET | `/api/v1/ventas/por-fecha` | Serie temporal de ventas |

### 📦 Inventario (Cassandra)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/inventario` | Inventario completo |
| GET | `/api/v1/inventario/alertas` | Items con stock crítico |
| GET | `/api/v1/inventario/por-almacen` | Resumen por almacén |

### 📊 KPIs (Combina ambas BDs)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/kpis` | Los 4 KPIs ejecutivos del dashboard |

---

<a name="cómo-funciona"></a>
## 5️⃣ Cómo Funciona Cada Pieza

### 🔧 `config.py` — La fuente única de verdad

```python
from api.config import settings

print(settings.MONGO_URI)        # mongodb://admin:password@localhost:27017/
print(settings.CASSANDRA_HOST)   # localhost
```

Lee variables del `.env` automáticamente. Si cambias `.env`, no tocas código.

### 🔌 `db/mongodb.py` y `db/cassandra.py` — Conexiones reutilizables

**Problema clásico**: abrir/cerrar una conexión a la BD en cada request es lentísimo.

**Solución**: una sola conexión que vive durante toda la vida del API:

```python
class MongoDB:
    client: MongoClient | None = None

    @classmethod
    def connect(cls):
        cls.client = MongoClient(...)   # Se llama 1 sola vez al arrancar

    @classmethod
    def get_collection(cls, name):
        return cls.client[settings.MONGO_DB][name]   # Se llama en cada request
```

### 🛣️ `routers/*.py` — Los endpoints

Cada archivo es una "mini-app" que se enfoca en un dominio:

```python
# routers/resenas.py
from fastapi import APIRouter

router = APIRouter(prefix="/resenas", tags=["Reseñas"])

@router.get("")
def listar_resenas(modelo: str | None = None):
    coleccion = MongoDB.get_collection("resenas_enriquecidas")
    filtro = {"modelo": modelo} if modelo else {}
    return list(coleccion.find(filtro, {"_id": 0}))
```

**Magia de FastAPI**:
- `modelo: str | None = None` → FastAPI lo convierte automáticamente en query parameter
- Si haces `GET /resenas?modelo=084`, `modelo` recibe `"084"` automáticamente
- Si haces `GET /resenas`, `modelo` recibe `None`

### 🎬 `main.py` — El director de orquesta

```python
app = FastAPI(...)                              # Crea la app

app.include_router(resenas.router, prefix="/api/v1")   # Conecta routers
app.include_router(ventas.router, prefix="/api/v1")
# etc...

@asynccontextmanager
async def lifespan(app):
    MongoDB.connect()         # Antes de aceptar requests
    CassandraDB.connect()
    yield                     # ← El API corre aquí
    MongoDB.disconnect()      # Al apagar
    CassandraDB.disconnect()
```

### 🔄 `db/serializers.py` — Convertir tipos especiales

MongoDB devuelve `ObjectId`, Cassandra devuelve `Decimal` y `Date`. Power BI no entiende esos tipos. Los convertimos:

```python
ObjectId("507f...")  →  "507f..."    (string)
datetime(2024,5,3)   →  "2024-05-03T00:00:00"   (ISO string)
Decimal("12.50")     →  12.5         (float)
```

---

<a name="probar"></a>
## 6️⃣ Probar la API

### Opción 1 — Swagger UI (la más cómoda)

1. Abre **http://localhost:8000/docs**
2. Verás todos los endpoints listados con su documentación.
3. Clic en cualquier endpoint → "Try it out" → "Execute".
4. Verás la respuesta JSON directamente en el navegador.

### Opción 2 — curl (terminal)

```bash
# Ver KPIs
curl http://localhost:8000/api/v1/kpis

# Ver reseñas del modelo 084
curl "http://localhost:8000/api/v1/resenas?modelo=084&limite=10"

# Ver alertas de stock
curl http://localhost:8000/api/v1/inventario/alertas
```

### Opción 3 — Navegador

Solo pega la URL en cualquier navegador:
```
http://localhost:8000/api/v1/ventas/por-sucursal
```

### Opción 4 — Postman / Insomnia / Thunder Client

Cualquier cliente HTTP funciona. Solo apuntas a `http://localhost:8000/api/v1/...`

---

<a name="conceptos"></a>
## 7️⃣ Conceptos Clave de FastAPI

### Decoradores `@router.get(...)`

```python
@router.get("/alertas")
def alertas_stockout():
    return {...}
```

El `@router.get("/alertas")` le dice a FastAPI:
> "Cuando alguien haga `GET /alertas`, ejecuta esta función"

### Type hints = validación automática

```python
def listar_ventas(limite: int = Query(100, ge=1, le=5000)):
    ...
```

- `int` → FastAPI valida que sea entero
- `ge=1` → debe ser ≥ 1
- `le=5000` → debe ser ≤ 5000
- Si alguien pone `?limite=abc`, FastAPI devuelve **error 422 automáticamente**

### Documentación auto-generada

FastAPI lee tus type hints, docstrings, y parámetros, y genera una documentación interactiva en `/docs`. **No tienes que escribirla a mano.**

### Async vs sync

Verás funciones con y sin `async def`. En nuestro API usamos funciones sync (`def`) porque pymongo y cassandra-driver son síncronos. **No hay problema**, FastAPI las maneja en threads automáticamente.

---

## 🎯 Próximos Pasos

Una vez que la API funciona localmente:

1. **Conectar Power BI** → Ver `GUIA_POWERBI.md`
2. **(Opcional) Agregar autenticación** → API keys o JWT
3. **(Opcional) Desplegar en la nube** → Render, Railway, AWS, Heroku

---

## 🛑 Troubleshooting

### Error: `address already in use`
El puerto 8000 está ocupado. Mata el proceso o cambia el puerto:
```bash
# Cambiar puerto en .env
API_PORT=8001
```

### Error: `MongoDB no está conectado`
Olvidaste levantar Docker:
```bash
docker-compose up -d mongodb cassandra
```

### Error: `NoHostAvailable` en Cassandra
Cassandra tarda en iniciar. Espera 60s después de `docker-compose up`.

### `ModuleNotFoundError: No module named 'fastapi'`
Tu entorno virtual no está activo, o no instalaste dependencias:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

📖 **Documentación oficial de FastAPI**: https://fastapi.tiangolo.com/
