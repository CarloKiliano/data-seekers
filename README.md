# 📊 Data Seekers: Revolución NoSQL para Panam

**Proyecto Final: Bases de Datos No Estructuradas | IIMAS UNAM**

> Consultora ficticia especializada en transformación digital de empresas de retail mediante arquitecturas NoSQL. Caso de estudio: **Panam (Empresa Mexicana de Calzado Deportivo)**.

---

## 🎯 Índice de Contenidos

1. [Visión Comercial](#visión-comercial)
2. [Los 3 Problemas Críticos](#los-3-problemas-críticos-y-soluciones)
3. [Arquitectura Técnica](#arquitectura-técnica)
4. [Estructura del Repositorio](#estructura-del-repositorio)
5. [Requisitos y Setup](#requisitos-y-setup)
6. [Fases del Proyecto](#fases-del-proyecto)
7. [Guía de Ejecución](#guía-de-ejecución)
8. [Equipo y Roles](#equipo-y-roles)
9. [Resultados Esperados](#resultados-esperados)

---

## 🚀 Visión Comercial

### El Pitch en 30 Segundos

**Panam enfrenta un problema crítico: está ciega a sus datos.**

- Genera miles de comentarios en redes sociales que NO procesa
- Produce inventario a ciegas, sin entender dónde vende y dónde acumula stock
- Toma decisiones ejecutivas 2 semanas después de que ocurren los eventos

**Resultado:** Competidores como Nike y Macy's ganan porque pivotan en 48 horas.

---

## 📋 Los 3 Problemas Críticos y Soluciones

### **Problema 1: "Desconexión Digital - No Escuchas a tu Mercado"**

**El Dolor:**
- Miles de reseñas, comentarios y sentimientos en redes (Instagram, TikTok, Twitter) están fragmentadas y sin procesar
- Panam NO sabe que los jóvenes quieren modelo 084 en rojo, o que el 125 tiene mala opinión
- Nike y Adidas predicen tendencias 3 meses antes; Panam se entera cuando no hay stock

**Solución NoSQL:**
- **MongoDB** captura y analiza cada comentario en tiempo real
- **Análisis de Sentimiento** clasifica automáticamente: sentimientos positivos/negativos, influencers, urgencias
- Algoritmos de NLP entrenan modelos específicos para lenguaje de calzado deportivo

**ROI Garantizado:**
- ✅ **+15-20% incremento en hits de producto** (alineación producción-demanda)
- ✅ **Menos devoluciones** (compran lo que realmente quieren)
- ✅ **Aumento de margen** (optimización de mix de productos)

---

### **Problema 2: "Caídas de Stock Impredecibles - Pierdes Dinero en Ambos Lados"**

**El Dolor:**
- Modelo 084 se agota viernes 3 PM en CDMX, pero Panam sigue produciendo fijo en Guadalajara
- En Monterrey, ese mismo modelo se acumula muerto
- Sin visibilidad en tiempo real: ¿Cuántos pares quedan en cada sucursal? ¿Cuándo va a faltar stock?
- Pierde ingresos por stockout + costos por sobreprodución/almacenamiento

**Solución NoSQL:**
- **Apache Cassandra** almacena series temporales de ventas por sucursal, modelo y hora (optimizado para lecturas <10ms)
- **Índices inteligentes** responden: "¿Stock del 084 en CDMX ahora?" en milisegundos
- **Predicción de Stockouts**: Algoritmo detecta 48h antes: "Se acaba el 084 en CDMX el viernes 6 PM"
- **Reabastecimiento automático**: Dispara órdenes sin intervención humana

**ROI Garantizado:**
- ✅ **-25-30% reducción en costos de inventario** (menos almacenamiento, mejor rotación)
- ✅ **+10-15% incremento en disponibilidad** (menos stockouts = más ventas)
- ✅ **Cientos de miles de pesos ahorrados anualmente**

---

### **Problema 3: "Decisiones Basadas en Intuición, No en Datos"**

**El Dolor:**
- Directiva de Panam decide qué fabricar, dónde invertir marketing, dónde abrir sucursal basándose en "corazonadas"
- Reportes Excel llegan 2 semanas después del evento
- Macy's y Amazon deciden en tiempo real con dashboards; Panam sigue lenta

**Solución NoSQL:**
- **Dashboard Ejecutivo en Power BI** conectado directamente a MongoDB y Cassandra
- **5 gráficos clave**: Ventas por región/modelo, Tendencias de sentimiento, Rotación de inventario, Predicción de demanda
- **4 KPIs críticos**: Tasa de conversión, Sentimiento promedio, Días de inventario, Margen por línea
- **3 filtros dinámicos**: Por región, modelo, período temporal (sin queries SQL)
- **Actualización en tiempo real**: Datos frescos cada 5 minutos

**ROI Garantizado:**
- ✅ **+20-25% mejora en precisión de decisiones**
- ✅ **-30% reducción de tiempo en reportería** (se acabó Excel)
- ✅ **Pivoteo en 48 horas, no en 2 semanas**
- ✅ **Liberación de 2-3 FTE** (personal de reporting)

---

### **Beneficio Acumulado: 50-75% Mejora Operativa**

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Días para pivote estratégico | 14 | 2 | ⬇️ 85% |
| Costo de inventario | 100% | 70% | ⬇️ 30% |
| Hits de producto | 100% | 120% | ⬆️ 20% |
| Precisión de decisiones | 100% | 125% | ⬆️ 25% |
| **Incremento en ventas** | Baseline | **+25-35%** | **⬆️ Estimado** |

---

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**

```
┌─────────────────────────────────────────────────────────────────┐
│                       TIER 1: DATA SOURCES                       │
│  (Simulados en Jupyter) ────────────────────────────────────────│
│  ├─ Reseñas de Redes Sociales (Instagram, TikTok, Twitter)      │
│  ├─ Tickets de Venta (POS) por sucursal                          │
│  ├─ Datos de Inventario (WMS)                                    │
│  └─ Eventos Web (carritos abandonados, búsquedas)                │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                TIER 2: ETL (Python/Pandas)                      │
│  (Jupyter Notebook - Ejecutable en Vivo) ─────────────────────│
│  ├─ Generador de Datos Masivos (Faker, Random)                 │
│  ├─ Transformación 1: Enriquecimiento con Sentimiento (TextBlob)│
│  ├─ Transformación 2: Agregación + Predicción de Stockouts     │
│  └─ Limpieza, validación y carga a BD                           │
└────────────────┬──────────────────────┬────────────────────────┘
                 │                      │
                 ▼                      ▼
    ┌────────────────────┐  ┌──────────────────────┐
    │  TIER 3a: MongoDB  │  │ TIER 3b: Cassandra   │
    │  (Documentos)      │  │ (Series Temporales)  │
    ├────────────────────┤  ├──────────────────────┤
    │ • Catálogo         │  │ • Ventas por hora    │
    │ • Reseñas          │  │ • Stock en tiempo    │
    │ • Eventos Web      │  │ • Predicciones       │
    │ • Análisis NLP     │  │ • Métricas agregadas │
    └────────┬───────────┘  └──────────┬───────────┘
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  TIER 4: Power BI Dashboard (Visualización)     │
    │  ├─ 5 Gráficos (Barras, Líneas, Scatter, Heat) │
    │  ├─ 4 KPIs (Highlights)                         │
    │  ├─ 1 Tabla de Resumen                          │
    │  └─ 3 Filtros Interactivos                      │
    └─────────────────────────────────────────────────┘
```

### **Bases de Datos NoSQL**

#### **MongoDB: Datos Semiestructurados**

```javascript
// Colección: productos
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "modelo": "084",
  "nombre": "Running Pro Elite",
  "categoria": "deportivo",
  "colores": ["negro", "blanco", "rojo", "azul"],
  "precio_base": 1200,
  "tallas": ["40", "41", "42", "43", "44", "45"],
  "especificaciones": {
    "material": "mesh + caucho",
    "amortiguacion": "gel",
    "peso_gramos": 250
  },
  "fecha_creacion": ISODate("2024-01-15T08:00:00Z")
}

// Colección: resenas
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "producto_id": ObjectId("507f1f77bcf86cd799439011"),
  "usuario": "sofiaZ_2024",
  "calificacion": 5,
  "comentario": "Increíble comodidad!!! Compré 2 pares más",
  "sentimiento": "positivo",
  "score_sentimiento": 0.89,
  "fuente": "instagram",
  "likes": 245,
  "es_influencer": true,
  "fecha": ISODate("2024-05-03T14:30:00Z")
}
```

#### **Apache Cassandra: Series Temporales**

```sql
CREATE KEYSPACE panam_ventas WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 3
};

-- Tabla optimizada para: "Dame ventas de modelo X en región Y"
CREATE TABLE panam_ventas.ventas_por_sucursal (
    sucursal TEXT,
    modelo TEXT,
    fecha DATE,
    hora_minuto TIMESTAMP,
    cantidad_vendida INT,
    ingresos DECIMAL,
    PRIMARY KEY ((sucursal, modelo), fecha, hora_minuto)
) WITH CLUSTERING ORDER BY (fecha DESC, hora_minuto DESC);

-- Tabla para inventario en tiempo real
CREATE TABLE panam_ventas.inventario_en_tiempo_real (
    almacen TEXT,
    modelo TEXT,
    talla TEXT,
    fecha DATE,
    hora TIMESTAMP,
    stock_actual INT,
    movimiento_tipo TEXT,
    PRIMARY KEY ((almacen, modelo, talla), fecha, hora)
) WITH CLUSTERING ORDER BY (fecha DESC, hora DESC);
```

---

## 📁 Estructura del Repositorio

```
data-seekers/
│
├── README.md (Este archivo)
├── .gitignore
├── docker-compose.yml (MongoDB + Cassandra + Jupyter)
│
├── 📂 data/
│   ├── resenas.csv (1,000 registros de reseñas simuladas)
│   ├── ventas.csv (5,000 registros de ventas)
│   ├── inventario.csv (2,000 registros de stock)
│   ├── eventos_web.csv (800 registros de comportamiento web)
│   └── README.md (Descripción de datasets)
│
├── 📂 notebooks/
│   ├── 01_generacion_datos.ipynb (Generador de datos masivos)
│   ├── 02_etl_transformaciones.ipynb (2 procesos de transformación)
│   ├── 03_mongodb_operaciones.ipynb (Índices, agregaciones en vivo)
│   ├── 04_cassandra_consultas.ipynb (Queries en tiempo real)
│   └── 05_analisis_exploratorio.ipynb (EDA completo)
│
├── 📂 scripts/
│   ├── setup_mongodb.js (Creación de colecciones e índices)
│   ├── setup_cassandra.cql (Creación de keyspace y tablas)
│   ├── carga_datos_mongodb.py (Script ETL → MongoDB)
│   └── carga_datos_cassandra.py (Script ETL → Cassandra)
│
├── 📂 dashboards/
│   ├── panam_powerbi.pbix (Dashboard en Power BI)
│   ├── INSTRUCCIONES_POWER_BI.md
│   └── screenshots/ (Capturas del dashboard)
│
├── 📂 presentacion/
│   ├── Data_Seekers_Pitch.pptx (Diapositivas ejecutivas)
│   ├── GUION_PRESENTACION.md (Script detallado por rol)
│   └── diagramas/ (Arquitectura, flujos, casos de uso)
│
├── 📂 documentacion/
│   ├── PLAN_TECNICO.md (Este documento, versión extendida)
│   ├── PLAN_COMERCIAL.md (Argumentos de venta, ROI)
│   ├── RÚBRICA_EVALUACION.md (Requisitos académicos)
│   └── PROBLEMAS_SOLUCIONADOS.md (Mapeo problema→solución)
│
└── 📂 logs/
    └── ejecutable_desde_presentacion.txt (Comandos y queries)
```

---

## 🛠️ Requisitos y Setup

### **Requisitos Previos**

- **Sistema Operativo**: Linux, macOS o Windows con WSL2
- **Docker Desktop**: v20.10+ ([Descargar](https://www.docker.com/products/docker-desktop))
- **Git**: v2.30+ ([Descargar](https://git-scm.com/))
- **Power BI Desktop** (opcional, para editar dashboard; versión: 2.120+)
- **Visual Studio Code** o **AntiGravity** (opcional, editor recomendado)

### **Instalación Rápida (5 minutos)**

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/data-seekers.git
cd data-seekers

# 2. Iniciar contenedores (MongoDB + Cassandra + Jupyter)
docker-compose up -d

# 3. Verificar que todo esté corriendo
docker ps

# Debería mostrar 3 contenedores activos:
# - panam_mongodb (Puerto 27017)
# - panam_cassandra (Puerto 9042)
# - panam_jupyter (Puerto 8888)

# 4. Acceder a Jupyter
# Abre en navegador: http://localhost:8888
# (Sin contraseña, ya está configurado en docker-compose.yml)

# 5. Navega a /work/notebooks/ y abre "01_generacion_datos.ipynb"
```

### **Verificación de Conectividad**

```python
# En Jupyter, ejecuta esto para verificar que todo está conectado:

# MongoDB
from pymongo import MongoClient
mongo_client = MongoClient('mongodb://admin:password@mongodb:27017/')
print(f"✓ MongoDB conectado: {mongo_client.server_info()}")

# Cassandra
from cassandra.cluster import Cluster
cassandra_cluster = Cluster(['cassandra'])
cassandra_session = cassandra_cluster.connect()
print("✓ Cassandra conectado")
```

---

## 📅 Fases del Proyecto

### **Fase 1: Arquitectura y Generación de Datos (Semana 1-2)**

**Entregables:**
- ✅ Esquemas definidos en MongoDB (4 colecciones)
- ✅ Tablas CQL creadas en Cassandra (3 tablas)
- ✅ Script `01_generacion_datos.ipynb` ejecutable
- ✅ 8,000+ registros simulados (reseñas, ventas, inventario, eventos web)
- ✅ Docker-compose.yml con 3 contenedores corriendo

**Tareas:**
```
[ ] Semana 1, Día 1-2: Setup Docker
[ ] Semana 1, Día 3-4: Crear esquemas MongoDB
[ ] Semana 1, Día 5: Crear tablas Cassandra
[ ] Semana 2, Día 1-2: Script generador de datos en Jupyter
[ ] Semana 2, Día 3-4: Validación de datos
[ ] Semana 2, Día 5: Documentación de esquemas
```

---

### **Fase 2: ETL y Consultas Avanzadas (Semana 2-3)**

**Entregables:**
- ✅ Notebook `02_etl_transformaciones.ipynb` con 2 procesos en vivo
  - Proceso 1: Enriquecimiento de reseñas con análisis de sentimiento
  - Proceso 2: Agregación de ventas + predicción de stockouts
- ✅ Notebook `03_mongodb_operaciones.ipynb` con índices y aggregations
- ✅ Notebook `04_cassandra_consultas.ipynb` con queries optimizadas
- ✅ Scripts de carga: `carga_datos_mongodb.py`, `carga_datos_cassandra.py`

**Tareas:**
```
[ ] Semana 2, Día 1: ETL Proceso 1 (TextBlob, sentimientos)
[ ] Semana 2, Día 2-3: ETL Proceso 2 (Predicción, alertas)
[ ] Semana 2, Día 4-5: MongoDB índices y aggregations
[ ] Semana 3, Día 1-2: Cassandra queries optimizadas
[ ] Semana 3, Día 3-4: Testing y optimización de performance
[ ] Semana 3, Día 5: Documentación de queries
```

---

### **Fase 3: Dashboard Power BI (Semana 3)**

**Entregables:**
- ✅ Archivo `panam_powerbi.pbix` con:
  - 5 gráficos (Barras, Líneas, Scatter, Tabla, Heatmap)
  - 4 KPIs (Highlights)
  - 1 tabla de resumen
  - 3 filtros interactivos
  - Conexión en vivo a MongoDB y Cassandra

**Tareas:**
```
[ ] Semana 3, Día 1: Conexión Power BI ↔ MongoDB
[ ] Semana 3, Día 1: Conexión Power BI ↔ Cassandra
[ ] Semana 3, Día 2-3: Diseño de 5 gráficos
[ ] Semana 3, Día 3-4: Diseño de 4 KPIs
[ ] Semana 3, Día 4: Tabla de resumen + filtros
[ ] Semana 3, Día 5: Refinamiento visual y validación
```

---

### **Fase 4: Presentación y Defensa (Semana 4)**

**Entregables:**
- ✅ Presentación `Data_Seekers_Pitch.pptx` (50 slides)
- ✅ Guion detallado `GUION_PRESENTACION.md` (por rol)
- ✅ Scripts ejecutables listos para demos en vivo

**Tareas:**
```
[ ] Semana 4, Día 1-2: Diseño de diapositivas
[ ] Semana 4, Día 2-3: Preparación de demos (ETL, BD, Dashboard)
[ ] Semana 4, Día 3-4: Ensayos por rol
[ ] Semana 4, Día 4-5: Integración de todos, ensayo técnico
[ ] Semana 4, Día 5: Presentación y defensa ante profesora
```

---

## 🚀 Guía de Ejecución

### **Ejecución de Fase 1: Generación de Datos**

```bash
# Terminal 1: Iniciar Docker
docker-compose up -d

# Terminal 2: Acceder a Jupyter
# Navega a http://localhost:8888
# Abre: notebooks/01_generacion_datos.ipynb
# Ejecuta celdas en orden:

# Celda 1: Imports
import pandas as pd
import numpy as np
from faker import Faker
# ... etc

# Celda 2: Configuración
fake = Faker('es_MX')
MODELS = ['084', '125', '200', '350']
# ... etc

# Celda 3-6: Generadores de datos
df_resenas = generar_resenas(1000)
df_ventas = generar_ventas(5000)
# ... etc

# Celda 7: Guardar CSVs
df_resenas.to_csv('data/resenas.csv', index=False)
# ... etc
```

### **Ejecución de Fase 2: ETL en Vivo (DEMO KEY)**

```python
# Abre: notebooks/02_etl_transformaciones.ipynb

# ===== TRANSFORMACIÓN 1: ANÁLISIS DE SENTIMIENTO =====
from textblob import TextBlob

def enriquecer_resenas(df):
    df['sentimiento_calculado'] = df['comentario'].apply(
        lambda x: "positivo" if TextBlob(str(x)).sentiment.polarity > 0.1 
                   else "negativo" if TextBlob(str(x)).sentiment.polarity < -0.1
                   else "neutro"
    )
    df['score_sentimiento'] = df['comentario'].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )
    return df

df_resenas_enriquecidas = enriquecer_resenas(df_resenas)
print(df_resenas_enriquecidas[['usuario', 'modelo', 'sentimiento_calculado', 'score_sentimiento']].head(10))

# Output esperado:
#           usuario modelo sentimiento_calculado  score_sentimiento
# 0        john_doe    084             positivo              0.75
# 1      sofiaZ_24    125             positivo              0.82
# 2      carlos_mx    200             negativo             -0.60
# ...

# ===== TRANSFORMACIÓN 2: PREDICCIÓN DE STOCKOUTS =====
def agregar_ventas_y_predecir(df_ventas, df_inventario):
    df_vendido = df_ventas.groupby(['sucursal', 'modelo'])['cantidad'].sum().reset_index()
    df_vendido.columns = ['sucursal', 'modelo', 'total_vendido']
    
    df_stock = df_inventario.groupby(['almacen', 'modelo'])['stock'].sum().reset_index()
    
    df_analisis = df_vendido.merge(
        df_stock,
        left_on=['sucursal', 'modelo'],
        right_on=['almacen', 'modelo'],
        how='left'
    )
    
    # ⚡ PREDICCIÓN
    df_analisis['dias_inventario'] = (df_analisis['stock'] / (df_analisis['total_vendido'] + 1)).astype(int)
    df_analisis['alerta_stockout'] = df_analisis['dias_inventario'] < 7
    
    return df_analisis

df_predicciones = agregar_ventas_y_predecir(df_ventas, df_inventario)
print(df_predicciones[df_predicciones['alerta_stockout'] == True])

# Output esperado:
#      sucursal modelo total_vendido  stock  dias_inventario  alerta_stockout
# 0  CDMX_Centro    084           230     45                0             True
# 1       Monterrey    125            95     12                0             True
# ...

print(f"\n⚠️ ALERTAS CRÍTICAS: {df_predicciones['alerta_stockout'].sum()} modelos con stockout en <7 días")
```

### **Ejecución de MongoDB en Vivo (DEMO KEY)**

```javascript
// Abre: notebooks/03_mongodb_operaciones.ipynb
// O usa mongosh en terminal

// 1. Crear índices
db.resenas.createIndex({ "modelo": 1, "sentimiento": 1, "fecha": -1 })
db.resenas.createIndex({ "comentario": "text", "fuente": 1 })

// 2. Aggregation Pipeline: Top 5 Modelos por Sentimiento Positivo
db.resenas.aggregate([
    { $match: { sentimiento: "positivo" } },
    { $group: {
        _id: "$modelo",
        cantidad_positivos: { $sum: 1 },
        promedio_likes: { $avg: "$likes" },
        es_influencer_count: { $sum: { $cond: ["$es_influencer", 1, 0] } }
    }},
    { $sort: { cantidad_positivos: -1 } },
    { $limit: 5 }
])

// Output esperado:
[
  { _id: '084', cantidad_positivos: 342, promedio_likes: 128, es_influencer_count: 15 },
  { _id: '350', cantidad_positivos: 298, promedio_likes: 112, es_influencer_count: 12 },
  { _id: '200', cantidad_positivos: 187, promedio_likes: 89, es_influencer_count: 7 },
  { _id: '125', cantidad_positivos: 173, promedio_likes: 73, es_influencer_count: 4 }
]
```

### **Ejecución de Cassandra en Vivo (DEMO KEY)**

```sql
-- Abre: notebooks/04_cassandra_consultas.ipynb
-- O usa cqlsh en terminal

-- 1. Query: Ventas de últimos 7 días por sucursal
SELECT sucursal, modelo, SUM(cantidad_vendida) as total_vendido
FROM panam_ventas.ventas_por_sucursal
WHERE sucursal = 'CDMX_Centro'
  AND fecha >= '2024-04-26'
  AND fecha <= '2024-05-03'
GROUP BY modelo
ORDER BY total_vendido DESC;

-- Output esperado:
--  sucursal      | modelo | total_vendido
-- ---------------+--------+---------------
--  CDMX_Centro   |    084 |           230
--  CDMX_Centro   |    350 |           156
--  CDMX_Centro   |    125 |            95
--  CDMX_Centro   |    200 |            45

-- 2. Query: Stock actual con alertas
SELECT almacen, modelo, talla, stock_actual
FROM panam_ventas.inventario_en_tiempo_real
WHERE almacen = 'Guadalajara'
  AND modelo = '084'
  AND fecha = '2024-05-03'
LIMIT 10;
```

### **Power BI Dashboard Execution**

```
1. Abre panam_powerbi.pbix en Power BI Desktop
2. Verifica conexiones:
   - Fuente 1: MongoDB (conexión JSON)
   - Fuente 2: Cassandra (ODBC o conectores)
3. Actualiza datos: Ctrl + Shift + R
4. Valida:
   - 5 gráficos rendering correctamente
   - 4 KPIs mostrando valores realistas
   - Filtros respondiendo
5. Exporta como PDF para presentación
```

---

## 👥 Equipo y Roles

| Rol | Persona | Responsabilidades | Tiempo Presentación |
|-----|---------|------------------|-------------------|
| **Arquitecto NoSQL** | Aldo | MongoDB/Cassandra, índices, agregaciones, schema design | 7 min teoría + 10 min demos |
| **Científico de Datos** | Carlo | ETL (Python), transformaciones, predicciones, ML | 8 min demos (2 procesos) |
| **Especialista Sentimiento** | José Julián | NLP, análisis de sentimiento, TextBlob, modelos | 5 min teoría + apoyo Carlo |
| **Director Comercial** | Isaac | Pitch, problemas/soluciones, ROI, cierre | 5 min intro + 3 min conclusión |
| **Ingeniero Visualización** | Leonardo | Power BI, dashboards, gráficos, UX/UI | 10 min demo dashboard |

### **Habilidades Requeridas por Rol**

**Aldo (Arquitecto)**
- [ ] MongoDB: crear colecciones, índices, aggregation pipeline
- [ ] Cassandra: CQL, tablas, partition keys, clustering keys
- [ ] Explicar cuándo usar qué BD (trade-offs)
- [ ] Responder preguntas sobre escalabilidad

**Carlo (Científico de Datos)**
- [ ] Python/Pandas: transformaciones, limpieza, validación
- [ ] Ejecutar 2 procesos en vivo sin errores
- [ ] Explicar algoritmos de predicción
- [ ] Responder sobre performance y optimización

**José Julián (Sentimiento)**
- [ ] TextBlob / NLP basics
- [ ] Explicar cómo se calcula sentimiento
- [ ] Interpretar scores (-1 a +1)
- [ ] Sugerir mejoras (BERT, GPT, etc.)

**Isaac (Comercial)**
- [ ] Dominar los 3 problemas y argumentos de venta
- [ ] Explicar ROI con números
- [ ] Responder objeciones ("¿Por qué no SQL?")
- [ ] Cerrar con call-to-action

**Leonardo (Visualización)**
- [ ] Power BI: conectar fuentes, crear medidas, DAX
- [ ] Explicar cada gráfico: qué mide, por qué
- [ ] Interactuar con filtros sin lag
- [ ] Responder sobre actualización de datos

---

## 📊 Resultados Esperados

### **Métricas de Éxito (Rúbrica)**

| Criterio | Peso | Evidencia |
|----------|------|-----------|
| **Arquitectura NoSQL** | 20% | MongoDB + Cassandra funcionando, índices creados en vivo |
| **ETL en Python** | 20% | 2 procesos ejecutados y explicados en vivo |
| **Bases de Datos en Vivo** | 20% | Colecciones, índices, queries ejecutadas en vivo |
| **Dashboard Power BI** | 20% | 5 gráficos + 4 KPIs + tabla + 3 filtros, conectado a BD |
| **Presentación Ejecutiva** | 10% | 50% texto / 50% visual, todos hablen |
| **Defensa Técnica** | 10% | Responder preguntas cruzadas sin titubear |

### **Números Esperados (Simulación)**

```
Datasets Generados:
  • 1,000 reseñas (MongoDB)
  • 5,000 transacciones de venta (Cassandra)
  • 2,000 registros de inventario (Cassandra)
  • 800 eventos web (MongoDB)
  • TOTAL: 8,800 registros realistas

Performance Esperado:
  • MongoDB: <50ms para aggregations
  • Cassandra: <10ms para queries de series temporales
  • Power BI: <1s para actualización de filtros

Métricas de Negocio (Simuladas):
  • Tasa de conversión: 4.2%
  • Sentimiento promedio: 0.71 (+0.1)
  • Días de inventario: 12 (alerta: <7)
  • Margen promedio: 42%
  • ROI estimado: 50-75% mejora operativa
```

---

## 📚 Documentación Adicional

- 📖 [PLAN_TECNICO.md](./documentacion/PLAN_TECNICO.md) - Detalles arquitectónicos
- 📖 [PLAN_COMERCIAL.md](./documentacion/PLAN_COMERCIAL.md) - Argumentos de venta completos
- 📖 [GUION_PRESENTACION.md](./presentacion/GUION_PRESENTACION.md) - Script palabra por palabra
- 📖 [RÚBRICA_EVALUACION.md](./documentacion/RÚBRICA_EVALUACION.md) - Requisitos académicos
- 📖 [TROUBLESHOOTING.md](./documentacion/TROUBLESHOOTING.md) - Solución de problemas

---

## 🔗 Enlaces Útiles

- [MongoDB Documentación](https://docs.mongodb.com/)
- [Cassandra Documentación](https://cassandra.apache.org/doc/)
- [TextBlob para Sentimientos](https://textblob.readthedocs.io/)
- [Power BI Learning](https://learn.microsoft.com/power-bi/)
- [Docker Tutorial](https://docker.com/)

---

## 📝 Licencia

Proyecto educativo para IIMAS UNAM. Uso interno únicamente.

---

## 👨‍💻 Autores

**Data Seekers - Consultora Ficticia**
- Aldo (Arquitecto de Datos NoSQL)
- Carlo (Científico de Datos)
- José Julián (Especialista en Análisis de Sentimiento)
- Isaac (Director de Estrategia Comercial)
- Leonardo (Ingeniero de Visualización)

---

## ✅ Checklist Final (Antes de Presentación)

```
ANTES DE ENTRAR AL AULA:

Fase 1 - Arquitectura:
  [ ] Docker-compose ejecutándose (3 contenedores UP)
  [ ] MongoDB accesible (conexión probada)
  [ ] Cassandra accesible (conexión probada)
  [ ] Jupyter corriendo sin errores

Fase 2 - ETL:
  [ ] Notebook 01 ejecutado: datos generados ✓
  [ ] Notebook 02 listo: 2 procesos sin errores
  [ ] Notebook 03 listo: índices y aggregations
  [ ] Notebook 04 listo: queries de Cassandra

Fase 3 - Dashboard:
  [ ] Power BI file abierto
  [ ] Conexiones validadas (MongoDB, Cassandra)
  [ ] 5 gráficos rendering
  [ ] 4 KPIs mostrando datos
  [ ] 3 filtros interactivos funcionan
  [ ] Pantalla 1080p+ (para demo clara)

Fase 4 - Presentación:
  [ ] Diapositivas completas (50 slides)
  [ ] Guion memorizado (cada rol)
  [ ] Comandos listos para copiar (no escribir en vivo)
  [ ] Preguntas esperadas (respuestas preparadas)
  [ ] Equipo alineado (ensayos completados)

Equipo Blindado:
  [ ] Aldo puede responder preguntas de Cassandra
  [ ] Carlo puede responder de NLP y predicciones
  [ ] José Julián puede explicar sentimiento
  [ ] Isaac cierra cualquier objeción comercial
  [ ] Leonardo explica cada métrica del dashboard

DURANTE LA PRESENTACIÓN:
  [ ] Grabar video de demos (para respaldos)
  [ ] Tener conexión a internet (MongoDB Atlas backup)
  [ ] Powerbank para laptops
  [ ] Micrófono si es aula grande
```

---

**Última Actualización:** Mayo 2024  
**Versión:** 1.0 - Release Inicial  
**Estado:** ✅ Listo para Presentación

---

> *"Data is the new oil, but only if you can refine it. En Data Seekers, refinamos datos NoSQL para ganar mercado."* — Isaac, Director Comercial
