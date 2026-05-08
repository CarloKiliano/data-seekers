# 🛠️ Guía de Instalación y Reproducibilidad

> Esta sección reemplaza / complementa la sección **"Requisitos y Setup"** del README principal.

---

## ✅ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

| Herramienta        | Versión mínima | Descarga                                                      |
| ------------------ | -------------- | ------------------------------------------------------------- |
| **Python**         | 3.10+          | [python.org](https://www.python.org/downloads/)               |
| **Docker Desktop** | 4.0+           | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git**            | 2.30+          | [git-scm.com](https://git-scm.com/)                           |

> **¿Por qué Docker?** MongoDB y Cassandra se levantan en contenedores para que no necesites instalarlos manualmente. Solo necesitas Docker.

---

## 🚀 Instalación en 4 Pasos

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/panam-nosql.git
cd panam-nosql
```

### Paso 2 — Ejecutar el script de setup

**macOS / Linux:**

```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**

```
Doble clic en setup.bat
```

El script hace automáticamente:

- ✅ Verifica que Python 3.10+ esté disponible
- ✅ Crea el entorno virtual `.venv`
- ✅ Instala todas las dependencias de `requirements.txt`
- ✅ Crea tu archivo `.env` desde la plantilla
- ✅ Verifica que Docker esté disponible

### Paso 3 — Levantar las bases de datos

```bash
# Levanta MongoDB (puerto 27017) y Cassandra (puerto 9042)
docker-compose up -d mongodb cassandra

# Verifica que estén corriendo:
docker ps
```

> ⏳ **Cassandra tarda ~30-60 segundos en inicializar.** Espera antes de ejecutar notebooks.

Para confirmar que Cassandra está lista:

```bash
docker logs panam_cassandra 2>&1 | tail -5
# Debe mostrar: "Starting listening for CQL clients"
```

### Paso 4 — Activar entorno y ejecutar notebooks

```bash
# Activar entorno virtual (si no está activo)
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows

# Lanzar Jupyter
jupyter notebook
```

Ejecuta los notebooks **en este orden**:

```
00_setup_inicial.ipynb          ← Verifica conexiones a BD
01_generacion_datos.ipynb       ← Genera los 8,800 registros
02_etl_transformaciones.ipynb   ← ETL + análisis de sentimiento
03_mongodb_operaciones_en_vivo.ipynb  ← Carga y queries MongoDB
04_cassandra_consultas.ipynb    ← Carga y queries Cassandra
```

---

## 🔧 Instalación Manual (sin el script)

Si prefieres hacerlo paso a paso:

```bash
# 1. Crear entorno virtual
python3 -m venv .venv

# 2. Activar
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env si tus puertos o credenciales son distintos
```

---

## ⚙️ Variables de Entorno

El archivo `.env` (creado automáticamente desde `.env.example`) controla la configuración:

| Variable             | Default                                     | Descripción                |
| -------------------- | ------------------------------------------- | -------------------------- |
| `MONGO_URI`          | `mongodb://admin:password@localhost:27017/` | URI de conexión a MongoDB  |
| `MONGO_DB`           | `panam_nosql`                               | Nombre de la base de datos |
| `CASSANDRA_HOST`     | `localhost`                                 | Host de Cassandra          |
| `CASSANDRA_PORT`     | `9042`                                      | Puerto CQL de Cassandra    |
| `CASSANDRA_KEYSPACE` | `panam_nosql`                               | Keyspace a usar            |

> ⚠️ **NUNCA subas `.env` a git.** Ya está en `.gitignore`. Solo sube `.env.example`.

---

## 🛑 Troubleshooting Común

### MongoDB no conecta

```bash
# Verifica que el contenedor esté corriendo
docker ps | grep panam_mongodb

# Si no aparece, revísalo:
docker logs panam_mongodb

# Reinicia:
docker-compose restart mongodb
```

### Cassandra se niega conexiones

```bash
# Cassandra tarda en iniciar. Verifica el log:
docker logs panam_cassandra 2>&1 | grep "Starting listening"

# Si no aparece, espera 30s más y reintenta
```

### Error de módulo no encontrado en Jupyter

```bash
# Asegúrate de que el kernel de Jupyter use el .venv correcto
pip install ipykernel
python -m ipykernel install --user --name=panam-nosql --display-name "Python (panam-nosql)"
# En Jupyter: Kernel → Change kernel → Python (panam-nosql)
```

### Conflicto de versiones de paquetes

```bash
# Recrea el entorno desde cero
deactivate
rm -rf .venv
./setup.sh
```

---

## 🗂️ Estructura de Archivos de Configuración

```
panam-nosql/
├── requirements.txt      ← Dependencias con versiones fijas (en git ✅)
├── .env.example          ← Plantilla de variables (en git ✅)
├── .env                  ← Tu configuración local (NO en git 🚫)
├── .gitignore            ← Archivos excluidos de git (en git ✅)
├── setup.sh              ← Instalación automática macOS/Linux (en git ✅)
└── setup.bat             ← Instalación automática Windows (en git ✅)
```
