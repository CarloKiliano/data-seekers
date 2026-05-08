#!/usr/bin/env python3
"""
Script de carga de datos a MongoDB para el proyecto Panam NoSQL.

Carga dos colecciones:
1. resenas_enriquecidas - Reseñas con análisis de sentimiento del ETL
2. eventos_web - Eventos de navegación en el sitio web

Uso:
    python carga_datos_mongodb.py

Variables de entorno opcionales:
    MONGO_URI - URI de conexión (default: mongodb://localhost:27017/)
    MONGO_DB  - Nombre de la base de datos (default: panam_nosql)
"""

import sys
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import pandas as pd
import os


def get_project_root(marker: str = "README.md") -> Path:
    """Sube por el árbol de directorios hasta encontrar el marcador de raíz."""
    current = Path(__file__).parent.resolve()
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"No se encontró la raíz del proyecto (buscando {marker}).")


def limpiar_documento(doc: dict) -> dict:
    """
    Limpia un documento para MongoDB:
    - Convierte NaN/None a None
    - Convierte tipos numpy a tipos nativos Python
    - Maneja fechas como strings (MongoDB las convierte a ISODate automáticamente)
    """
    import numpy as np
    
    cleaned = {}
    for k, v in doc.items():
        # NaN -> None
        if isinstance(v, float) and (pd.isna(v) or v != v):  # v != v detecta NaN
            cleaned[k] = None
        # Numpy int/float -> Python int/float
        elif isinstance(v, (np.integer, np.int64)):
            cleaned[k] = int(v)
        elif isinstance(v, (np.floating, np.float64)):
            cleaned[k] = float(v)
        # Numpy bool -> Python bool
        elif isinstance(v, np.bool_):
            cleaned[k] = bool(v)
        # Dejar todo lo demás como está
        else:
            cleaned[k] = v
    
    return cleaned


def cargar_resenas(db, data_path: Path) -> int:
    """Carga reseñas enriquecidas a MongoDB."""
    
    print("\n" + "="*70)
    print("📝 CARGANDO RESEÑAS ENRIQUECIDAS")
    print("="*70)
    
    # Leer CSV
    csv_path = data_path / "resenas_enriquecidas.csv"
    
    if not csv_path.exists():
        print(f"⚠️  Advertencia: {csv_path} no existe")
        print("   Ejecuta primero: 02_etl_transformaciones.ipynb")
        return 0
    
    print(f"\n📂 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   ✅ {len(df)} registros leídos")
    
    # Convertir a lista de diccionarios limpios
    print("\n🧹 Limpiando documentos...")
    documentos = [limpiar_documento(row) for row in df.to_dict('records')]
    print(f"   ✅ {len(documentos)} documentos preparados")
    
    # Insertar en MongoDB
    collection = db['resenas_enriquecidas']
    
    # Limpiar colección existente
    print(f"\n🗑️  Limpiando colección existente...")
    result = collection.delete_many({})
    print(f"   ✅ {result.deleted_count} documentos eliminados")
    
    # Inserción por lotes (más eficiente para grandes volúmenes)
    print(f"\n💾 Insertando documentos...")
    batch_size = 1000
    total_insertados = 0
    
    try:
        for i in range(0, len(documentos), batch_size):
            batch = documentos[i:i+batch_size]
            result = collection.insert_many(batch, ordered=False)
            total_insertados += len(result.inserted_ids)
            print(f"   ⏳ Insertados {total_insertados}/{len(documentos)}...", end='\r')
        
        print(f"\n   ✅ {total_insertados} documentos insertados correctamente")
        
    except BulkWriteError as e:
        print(f"\n   ⚠️  Error parcial en inserción: {len(e.details['writeErrors'])} documentos fallaron")
        total_insertados = e.details['nInserted']
    """
    # Crear índices para optimizar consultas
    print(f"\n🔍 Creando índices...")
    
    indices = [
        ('modelo', 1),
        ('sentimiento_calculado', 1),
        ('fecha', -1),  # -1 = descendente
        ('calificacion', 1),
        ('fuente', 1),
    ]
    
    for campo, orden in indices:
        collection.create_index([(campo, orden)])
        print(f"   ✅ Índice creado en '{campo}'")
    
    # Índice compuesto para consultas frecuentes
    collection.create_index([('modelo', 1), ('sentimiento_calculado', 1)])
    print(f"   ✅ Índice compuesto creado en 'modelo' + 'sentimiento_calculado'")
    """
    
    # Verificación final
    count = collection.count_documents({})
    print(f"\n📊 Verificación final: {count} documentos en la colección")
    
    return total_insertados


def cargar_eventos(db, data_path: Path) -> int:
    """Carga eventos web a MongoDB."""
    
    print("\n" + "="*70)
    print("🌐 CARGANDO EVENTOS WEB")
    print("="*70)
    
    # Leer CSV
    csv_path = data_path / "eventos.csv"
    
    if not csv_path.exists():
        print(f"⚠️  Advertencia: {csv_path} no existe")
        print("   Ejecuta primero: 01_generacion_datos.ipynb")
        return 0
    
    print(f"\n📂 Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   ✅ {len(df)} registros leídos")
    
    # Convertir a lista de diccionarios limpios
    print("\n🧹 Limpiando documentos...")
    documentos = [limpiar_documento(row) for row in df.to_dict('records')]
    print(f"   ✅ {len(documentos)} documentos preparados")
    
    # Insertar en MongoDB
    collection = db['eventos_web']
    
    # Limpiar colección existente
    print(f"\n🗑️  Limpiando colección existente...")
    result = collection.delete_many({})
    print(f"   ✅ {result.deleted_count} documentos eliminados")
    
    # Inserción
    print(f"\n💾 Insertando documentos...")
    
    try:
        result = collection.insert_many(documentos, ordered=False)
        total_insertados = len(result.inserted_ids)
        print(f"   ✅ {total_insertados} documentos insertados correctamente")
        
    except BulkWriteError as e:
        print(f"   ⚠️  Error parcial: {len(e.details['writeErrors'])} documentos fallaron")
        total_insertados = e.details['nInserted']
    
    """# Crear índices
    print(f"\n🔍 Creando índices...")
    
    indices = [
        ('evento_tipo', 1),
        ('modelo', 1),
        ('fecha', -1),
        ('dispositivo', 1),
    ]
    
    for campo, orden in indices:
        collection.create_index([(campo, orden)])
        print(f"   ✅ Índice creado en '{campo}'")
    
    # Índice compuesto
    collection.create_index([('usuario_id', 1), ('fecha', -1)])
    print(f"   ✅ Índice compuesto creado en 'usuario_id' + 'fecha'")
    """
    
    # Verificación final
    count = collection.count_documents({})
    print(f"\n📊 Verificación final: {count} documentos en la colección")
    
    return total_insertados


def main():
    """Función principal."""
    
    print("="*70)
    print("🚀 CARGA DE DATOS A MONGODB")
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
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:password@localhost:27017/')
    DB_NAME = os.getenv('MONGO_DB', 'panam_nosql')
    
    print(f"\n🔌 Conectando a MongoDB...")
    print(f"   URI: {MONGO_URI}")
    print(f"   Base de datos: {DB_NAME}")
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Verificar conexión
        db = client[DB_NAME]
        print(f"   ✅ Conexión exitosa")
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("   Verifica que MongoDB esté corriendo.")
        sys.exit(1)
    
    # Cargar datos
    try:
        total_resenas = cargar_resenas(db, DATA_PATH)
        total_eventos = cargar_eventos(db, DATA_PATH)
        
        # Resumen final
        print("\n" + "="*70)
        print("✅ CARGA COMPLETADA")
        print("="*70)
        print(f"\n📊 Resumen:")
        print(f"   - Reseñas enriquecidas: {total_resenas:>5} documentos")
        print(f"   - Eventos web:          {total_eventos:>5} documentos")
        print(f"   - TOTAL:                {total_resenas + total_eventos:>5} documentos")
        print(f"\n💡 Siguiente paso: ejecutar 03_mongodb_operaciones.ipynb")
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        client.close()


if __name__ == "__main__":
    main()
