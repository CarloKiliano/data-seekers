#!/usr/bin/env python3
"""
Script de carga de datos a Cassandra para el proyecto Panam NoSQL.

Carga dos tablas:
1. ventas_por_sucursal - Ventas históricas por sucursal y fecha
2. inventario_por_almacen - Movimientos de inventario por almacén

Uso:
    python carga_datos_cassandra.py

Variables de entorno opcionales:
    CASSANDRA_HOST - Host de Cassandra (default: localhost)
    CASSANDRA_PORT - Puerto de Cassandra (default: 9042)
    CASSANDRA_KEYSPACE - Keyspace a usar (default: panam_nosql)
"""

import sys
from pathlib import Path
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, ConsistencyLevel
import pandas as pd
import os
from datetime import datetime, time


def get_project_root(marker: str = "README.md") -> Path:
    """Sube por el árbol de directorios hasta encontrar el marcador de raíz."""
    current = Path(__file__).parent.resolve()
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"No se encontró la raíz del proyecto (buscando {marker}).")


def cargar_ventas(session, data_path: Path) -> int:
    """Carga ventas a Cassandra."""
    
    print("\n" + "="*70)
    print("💰 CARGANDO VENTAS POR SUCURSAL")
    print("="*70)
    
    # Leer CSV
    csv_path = data_path / "ventas.csv"
    
    if not csv_path.exists():
        print(f"⚠️  Advertencia: {csv_path} no existe")
        print("   Ejecuta primero: 01_generacion_datos.ipynb")
        return 0
    
    print(f"\n📂 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   ✅ {len(df)} registros leídos")
    
    # Limpiar datos
    print(f"\n🧹 Preparando datos...")
    
    # Convertir fecha string a date object
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    
    # Convertir hora string a time object (Cassandra necesita time, no string)
    if df['hora'].dtype == 'object':
        df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time
    
    # Limpiar precio_unitario (convertir a Decimal para Cassandra)
    from decimal import Decimal
    df['precio_unitario'] = df['precio_unitario'].apply(lambda x: Decimal(str(x)))
    
    print(f"   ✅ Datos preparados")
    
    # Limpiar tabla existente
    print(f"\n🗑️  Limpiando tabla existente...")
    session.execute("TRUNCATE ventas_por_sucursal")
    print(f"   ✅ Tabla truncada")
    
    # Preparar statement
    insert_query = """
    INSERT INTO ventas_por_sucursal (
        sucursal, fecha, modelo, talla, hora, cantidad,
        precio_unitario, descuento_pct, metodo_pago, tipo_cliente, vendedor
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(insert_query)
    
    # Inserción por lotes (más eficiente)
    print(f"\n💾 Insertando registros...")
    batch_size = 100  # Cassandra recomienda batches pequeños
    total_insertados = 0
    errores = 0
    
    for i in range(0, len(df), batch_size):
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
        batch_df = df.iloc[i:i+batch_size]
        
        for _, row in batch_df.iterrows():
            try:
                batch.add(prepared, (
                    row['sucursal'],
                    row['fecha'],
                    row['modelo'],
                    int(row['talla']),
                    row['hora'],
                    int(row['cantidad']),
                    row['precio_unitario'],
                    int(row['descuento_pct']),
                    row['metodo_pago'],
                    row['tipo_cliente'],
                    row['vendedor']
                ))
            except Exception as e:
                print(f"\n   ⚠️  Error en fila {i}: {e}")
                errores += 1
                continue
        
        try:
            session.execute(batch)
            total_insertados += len(batch_df) - errores
            print(f"   ⏳ Insertados {total_insertados}/{len(df)}...", end='\r')
        except Exception as e:
            print(f"\n   ⚠️  Error en batch: {e}")
            errores += len(batch_df)
    
    print(f"\n   ✅ {total_insertados} registros insertados correctamente")
    
    if errores > 0:
        print(f"   ⚠️  {errores} registros fallaron")
    
    # Verificación final
    count_query = "SELECT COUNT(*) FROM ventas_por_sucursal"
    result = session.execute(count_query).one()
    # Cassandra COUNT puede ser aproximado en tablas grandes
    print(f"\n📊 Verificación: ~{result.count} registros en la tabla")
    
    return total_insertados


def cargar_inventario(session, data_path: Path) -> int:
    """Carga inventario a Cassandra."""
    
    print("\n" + "="*70)
    print("📦 CARGANDO INVENTARIO POR ALMACÉN")
    print("="*70)
    
    # Leer CSV
    csv_path = data_path / "inventario.csv"
    
    if not csv_path.exists():
        print(f"⚠️  Advertencia: {csv_path} no existe")
        print("   Ejecuta primero: 01_generacion_datos.ipynb")
        return 0
    
    print(f"\n📂 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   ✅ {len(df)} registros leídos")
    
    # Limpiar datos
    print(f"\n🧹 Preparando datos...")
    
    # Convertir fecha string a date object
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    
    print(f"   ✅ Datos preparados")
    
    # Limpiar tabla existente
    print(f"\n🗑️  Limpiando tabla existente...")
    session.execute("TRUNCATE inventario_por_almacen")
    print(f"   ✅ Tabla truncada")
    
    # Preparar statement
    insert_query = """
    INSERT INTO inventario_por_almacen (
        almacen, modelo, talla, fecha, stock,
        capacidad_max, movimiento, punto_reorden
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(insert_query)
    
    # Inserción por lotes
    print(f"\n💾 Insertando registros...")
    batch_size = 100
    total_insertados = 0
    errores = 0
    
    for i in range(0, len(df), batch_size):
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
        batch_df = df.iloc[i:i+batch_size]
        
        for _, row in batch_df.iterrows():
            try:
                batch.add(prepared, (
                    row['almacen'],
                    row['modelo'],
                    int(row['talla']),
                    row['fecha'],
                    int(row['stock']),
                    int(row['capacidad_max']),
                    row['movimiento'],
                    int(row['punto_reorden'])
                ))
            except Exception as e:
                print(f"\n   ⚠️  Error en fila {i}: {e}")
                errores += 1
                continue
        
        try:
            session.execute(batch)
            total_insertados += len(batch_df) - errores
            print(f"   ⏳ Insertados {total_insertados}/{len(df)}...", end='\r')
        except Exception as e:
            print(f"\n   ⚠️  Error en batch: {e}")
            errores += len(batch_df)
    
    print(f"\n   ✅ {total_insertados} registros insertados correctamente")
    
    if errores > 0:
        print(f"   ⚠️  {errores} registros fallaron")
    
    # Verificación final
    count_query = "SELECT COUNT(*) FROM inventario_por_almacen"
    result = session.execute(count_query).one()
    print(f"\n📊 Verificación: ~{result.count} registros en la tabla")
    
    return total_insertados


def main():
    """Función principal."""
    
    print("="*70)
    print("🚀 CARGA DE DATOS A CASSANDRA")
    print("   Proyecto: Panam NoSQL - Data Seekers")
    print("="*70)
    
    # Obtener rutas
    try:
        PROJECT_ROOT = get_project_root()
        DATA_PATH = PROJECT_ROOT / "data"
        print(f"\n📂 Raíz del proyecto: {PROJECT_ROOT}")
        print(f"📂 Carpeta de datos:  {DATA_PATH}")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Asegúrate de ejecutar este script desde dentro del proyecto.")
        sys.exit(1)
    
    # Configuración de conexión
    CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'localhost')
    CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
    KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'panam_nosql')
    
    print(f"\n🔌 Conectando a Cassandra...")
    print(f"   Host: {CASSANDRA_HOST}")
    print(f"   Puerto: {CASSANDRA_PORT}")
    print(f"   Keyspace: {KEYSPACE}")
    
    try:
        cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
        session = cluster.connect()
        session.set_keyspace(KEYSPACE)
        print(f"   ✅ Conexión exitosa")
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("   Verifica que Cassandra esté corriendo.")
        print("   Si acabas de iniciar Cassandra, espera 30-60 segundos.")
        sys.exit(1)
    
    # Cargar datos
    try:
        total_ventas = cargar_ventas(session, DATA_PATH)
        total_inventario = cargar_inventario(session, DATA_PATH)
        
        # Resumen final
        print("\n" + "="*70)
        print("✅ CARGA COMPLETADA")
        print("="*70)
        print(f"\n📊 Resumen:")
        print(f"   - Ventas por sucursal:     {total_ventas:>5} registros")
        print(f"   - Inventario por almacén:  {total_inventario:>5} registros")
        print(f"   - TOTAL:                   {total_ventas + total_inventario:>5} registros")
        print(f"\n💡 Siguiente paso: ejecutar 04_cassandra_consultas.ipynb")
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        cluster.shutdown()


if __name__ == "__main__":
    main()
