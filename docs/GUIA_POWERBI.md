# 🔌 Guía: Conectar Power BI a la API

> Esta guía explica paso a paso cómo importar datos del API a Power BI Desktop.
> Asume que la API ya está corriendo en `http://localhost:8000`.

---

## 📑 Tabla de Contenidos

1. [Prerrequisitos](#prerrequisitos)
2. [Conectar al endpoint principal](#conectar)
3. [Importar múltiples endpoints](#múltiples)
4. [Configurar actualización automática](#actualización)
5. [Crear medidas y KPIs](#kpis)
6. [Troubleshooting](#troubleshooting)

---

<a name="prerrequisitos"></a>
## 1️⃣ Prerrequisitos

Antes de empezar, asegúrate de que:

- ✅ La API está corriendo: `python run_api.py`
- ✅ Los datos están cargados en MongoDB y Cassandra:
  ```bash
  python carga_datos_mongodb.py
  python carga_datos_cassandra.py
  ```
- ✅ Puedes ver datos en el navegador: http://localhost:8000/api/v1/kpis
- ✅ Tienes **Power BI Desktop** instalado (versión gratuita está bien)

---

<a name="conectar"></a>
## 2️⃣ Conectar al Endpoint Principal (Tu Primer Dataset)

### Paso 1 — Abrir Power BI y crear conexión Web

1. Abre Power BI Desktop
2. En la cinta superior: **Inicio → Obtener datos → Web**

   ![Obtener datos Web](https://learn.microsoft.com/en-us/power-bi/connect-data/media/desktop-connect-to-web/connect-web-1.png)

### Paso 2 — Pegar la URL del endpoint

En el cuadro de diálogo:
- Selecciona **Básica**
- URL: `http://localhost:8000/api/v1/ventas`
- Clic en **Aceptar**

### Paso 3 — Confirmar acceso anónimo

Power BI te preguntará cómo autenticarse. Selecciona:
- **Anónimo** (la API no tiene autenticación por ahora)
- Clic en **Conectar**

### Paso 4 — Convertir JSON a tabla

Power BI abre el **Editor de Power Query** y muestra una lista. Ahora hay que convertirla a tabla:

1. Si ves "List" → clic en **A la tabla** (en la cinta superior)
2. En el diálogo, deja los valores por defecto → **Aceptar**
3. Verás una columna llamada `Column1` con valores tipo "Record"
4. Clic en el icono de **expandir** (↔️) en el header de la columna
5. Desmarca "Usar el nombre de columna original como prefijo"
6. Clic en **Aceptar**

🎉 **¡Ya tienes los datos como tabla!**

### Paso 5 — Cargar a Power BI

- Clic en **Cerrar y aplicar** (esquina superior izquierda)
- Power BI cargará los datos y los tendrás disponibles para crear visualizaciones

---

<a name="múltiples"></a>
## 3️⃣ Importar Múltiples Endpoints

Para un dashboard completo necesitas varios datasets. Repite el proceso para cada endpoint:

### Endpoints recomendados para el dashboard

| URL | Para qué gráfica |
|---|---|
| `http://localhost:8000/api/v1/ventas` | Tabla principal de ventas |
| `http://localhost:8000/api/v1/ventas/por-sucursal` | Gráfica de barras: ventas por región |
| `http://localhost:8000/api/v1/ventas/por-modelo` | Gráfica: modelos más vendidos |
| `http://localhost:8000/api/v1/ventas/por-fecha` | Gráfica de líneas: tendencia temporal |
| `http://localhost:8000/api/v1/resenas` | Tabla de reseñas individuales |
| `http://localhost:8000/api/v1/resenas/por-modelo` | Sentimiento por modelo |
| `http://localhost:8000/api/v1/resenas/tendencia-sentimiento` | Tendencia de sentimiento |
| `http://localhost:8000/api/v1/inventario` | Tabla de inventario |
| `http://localhost:8000/api/v1/inventario/alertas` | Tabla de alertas (stock crítico) |
| `http://localhost:8000/api/v1/eventos/conversion` | Tasa de conversión |
| `http://localhost:8000/api/v1/kpis` | Los 4 KPIs principales |

### Para agregar más datasets

En Power BI Desktop:
1. **Inicio → Transformar datos → Editor de Power Query**
2. **Inicio → Nuevo origen → Web**
3. Pega la siguiente URL y repite el proceso de conversión a tabla
4. Cada dataset aparecerá como una tabla separada en el panel derecho

### Renombrar las tablas para que sean legibles

Después de importar cada endpoint, en el panel derecho:
- Clic derecho sobre `Query1` → Renombrar → `ventas`
- Clic derecho sobre `Query2` → Renombrar → `ventas_por_sucursal`
- etc.

---

<a name="actualización"></a>
## 4️⃣ Configurar Actualización de Datos

### Actualización Manual (recomendado durante desarrollo)

En Power BI Desktop:
- **Inicio → Actualizar** (o `Ctrl + Shift + R`)
- Power BI vuelve a llamar a la API y trae los datos frescos

### Actualización Programada (Power BI Service)

Si publicas el dashboard a Power BI Service (la versión web), necesitarás un **Gateway** porque tu API corre en `localhost`. Para presentación local, la actualización manual es suficiente.

---

<a name="kpis"></a>
## 5️⃣ Crear Medidas y KPIs

### Ejemplo: Tarjeta de "Ingresos Totales"

1. En la pestaña **Reporte**, selecciona **Tarjeta** (visualización)
2. Arrastra el campo `total_ingresos` de la tabla `ventas_por_sucursal` al área de "Campos"
3. Power BI mostrará la suma automáticamente

### Ejemplo: Gráfico de barras "Ventas por Sucursal"

1. Selecciona **Gráfico de barras agrupadas**
2. **Eje Y**: `sucursal` (de tabla `ventas_por_sucursal`)
3. **Eje X**: `total_ingresos`
4. Listo

### Ejemplo: Mapa de calor de sentimiento

1. Selecciona **Tabla** o **Matriz**
2. **Filas**: `modelo` (de tabla `resenas_por_modelo`)
3. **Valores**: `score_sentimiento_promedio`
4. **Formato condicional** → Color de fondo → Por valor
5. Configura: rojo (negativo) → amarillo → verde (positivo)

### Filtros dinámicos

1. Inserta una **Segmentación de datos** (slicer)
2. Arrastra `modelo` al slicer
3. Power BI filtrará automáticamente todas las gráficas conectadas

---

<a name="troubleshooting"></a>
## 6️⃣ Troubleshooting

### ❌ "No se puede conectar al servidor remoto"

**Causa**: La API no está corriendo.

**Solución**:
```bash
python run_api.py
```
Verifica que ves: `✅ MongoDB conectado` y `✅ Cassandra conectado`.

### ❌ "Acceso denegado" o "Credenciales no válidas"

**Causa**: Power BI está intentando autenticarse cuando la API es anónima.

**Solución**:
- En Power BI: **Archivo → Opciones → Configuración del origen de datos**
- Encuentra `http://localhost:8000`
- Clic en **Editar permisos** → Selecciona **Anónimo**

### ❌ "El JSON contiene un valor que no se puede convertir"

**Causa**: Algún tipo de dato no se serializó bien.

**Solución**: La API ya maneja esto, pero si aparece, revisa que `serializers.py` esté funcionando. Visita el endpoint en el navegador para ver el JSON crudo.

### ❌ Power BI carga muy lento

**Causa**: Estás importando un endpoint con muchos datos sin límite.

**Solución**: Usa el parámetro `limite`:
```
http://localhost:8000/api/v1/ventas?limite=500
```

### ❌ "Es posible que necesite ajustar la consulta web"

**Causa**: Power BI no detectó automáticamente que es JSON.

**Solución**: En el editor de Power Query, agrega manualmente esta línea al inicio:
```m
Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/ventas"))
```

### ❌ Datos no se actualizan al refrescar

**Causa**: Caché de Power BI.

**Solución**: 
- **Archivo → Opciones → Datos cargados → Borrar caché**
- O reinicia Power BI Desktop

---

## 📊 Estructura Recomendada del Dashboard

Basado en los 5 gráficos + 4 KPIs del proyecto:

```
┌─────────────────────────────────────────────────────────────┐
│  PANAM — Dashboard Ejecutivo                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │ Ventas │  │ Conv.  │  │ Sent.  │  │ Stock  │  ← KPIs    │
│  │ $XX K  │  │  X.X%  │  │  0.71  │  │  XX⚠️  │            │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Ventas por Sucursal  │  │ Modelos más vendidos │        │
│  │ (barras)             │  │ (barras horizontales)│        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Tendencia ventas     │  │ Tendencia sentimiento│        │
│  │ (líneas temporales)  │  │ (líneas temporales)  │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Alertas de Stockout (tabla con formato condicional)│    │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  Filtros: [Modelo ▼] [Sucursal ▼] [Periodo ▼]              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Tip Pro: URL Parameters en Power BI

Power BI permite pasar parámetros a las URLs. Útil si quieres hacer dashboards filtrados:

```
http://localhost:8000/api/v1/ventas?modelo=084
http://localhost:8000/api/v1/resenas?sentimiento=positivo
```

Puedes crear un parámetro dinámico en Power Query y dejar que el usuario elija qué modelo ver.

---

## ✅ Checklist Final

Antes de la presentación:

- [ ] API corriendo (`python run_api.py`)
- [ ] Health check OK (`http://localhost:8000/health`)
- [ ] 11 endpoints importados a Power BI
- [ ] 5 gráficos creados
- [ ] 4 KPIs en tarjetas
- [ ] 3 filtros (slicers) configurados
- [ ] Probaste actualizar datos (`Ctrl + Shift + R`)
- [ ] Guardaste el archivo `.pbix`

🚀 **¡Tu dashboard está listo para impresionar!**
