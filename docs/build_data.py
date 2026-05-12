#!/usr/bin/env python3
"""
build_data.py
-------------
Convierte los CSVs del proyecto (data/ventas.csv, data/resenas.csv) en el JSON
que consume el dashboard HTML modular (docs/data/panam_data.json).

Estrategia: sampling estadísticamente representativo + factor de escala,
para mantener el JSON ligero (<1 MB) sin perder fidelidad en agregados.

Uso (desde la raíz del repo):
    python docs/build_data.py
    python docs/build_data.py --csv-dir data/ --out docs/data/panam_data.json
    python docs/build_data.py --sample-ventas 10000 --sample-resenas 3000
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Convierte CSVs Panam a JSON del dashboard.")
    parser.add_argument('--csv-dir', default='data', help="Carpeta con los CSVs (default: data/)")
    parser.add_argument('--out', default='docs/data/panam_data.json',
                        help="Archivo de salida JSON")
    parser.add_argument('--sample-ventas', type=int, default=5000,
                        help="Tamaño de sample para ventas (default 5000)")
    parser.add_argument('--sample-resenas', type=int, default=2000,
                        help="Tamaño de sample para reseñas (default 2000)")
    parser.add_argument('--seed', type=int, default=42, help="Random seed")
    args = parser.parse_args()

    csv_dir = Path(args.csv_dir)
    ventas_path = csv_dir / 'ventas.csv'
    resenas_path = csv_dir / 'resenas.csv'

    if not ventas_path.exists() or not resenas_path.exists():
        print(f"❌ No se encontraron los CSVs en {csv_dir}/")
        print(f"   Esperaba: ventas.csv, resenas.csv")
        print(f"   Genera los datos primero con:")
        print(f"     python scripts/generar_datos_masivos.py --escala full")
        return 1

    print(f"📂 Leyendo {ventas_path}...")
    ventas = pd.read_csv(ventas_path, parse_dates=['fecha'])
    print(f"📂 Leyendo {resenas_path}...")
    resenas = pd.read_csv(resenas_path, parse_dates=['fecha'])

    # Columnas derivadas
    ventas['ingreso'] = (
        ventas['cantidad'] * ventas['precio_unitario'] * (1 - ventas['descuento_pct'] / 100)
    )
    ventas['estado'] = ventas['sucursal'].str.split('_').str[0]

    # Sampling reproducible
    n_v = min(args.sample_ventas, len(ventas))
    n_r = min(args.sample_resenas, len(resenas))
    ventas_sample = ventas.sample(n=n_v, random_state=args.seed).copy()
    resenas_sample = resenas.sample(n=n_r, random_state=args.seed).copy()

    ventas_sample['fecha'] = ventas_sample['fecha'].dt.strftime('%Y-%m-%d')
    resenas_sample['fecha'] = resenas_sample['fecha'].dt.strftime('%Y-%m-%d')

    scale_v = len(ventas) / n_v
    scale_r = len(resenas) / n_r

    ventas_export = ventas_sample[[
        'fecha', 'estado', 'modelo', 'talla',
        'cantidad', 'precio_unitario', 'descuento_pct',
        'ingreso', 'metodo_pago'
    ]].copy()
    ventas_export['ingreso'] = ventas_export['ingreso'].round(2)

    out = {
        'meta': {
            'total_ventas': int(len(ventas)),
            'total_resenas': int(len(resenas)),
            'sample_ventas': n_v,
            'sample_resenas': n_r,
            'scale_v': round(scale_v, 4),
            'scale_r': round(scale_r, 4),
            'fecha_min': ventas['fecha'].min().strftime('%Y-%m-%d'),
            'fecha_max': ventas['fecha'].max().strftime('%Y-%m-%d'),
        },
        'estados': sorted(ventas['estado'].unique().tolist()),
        'modelos': sorted(ventas['modelo'].unique().tolist()),
        'ventas': ventas_export.to_dict('records'),
        'resenas': resenas_sample[['fecha', 'modelo', 'calificacion']].to_dict('records'),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = out_path.stat().st_size / 1024
    print(f"\n✅ Generado: {out_path} ({size_kb:.0f} KB)")
    print(f"   Total real: {len(ventas):,} ventas, {len(resenas):,} reseñas")
    print(f"   Sample:     {n_v:,} ventas, {n_r:,} reseñas")
    print(f"   Escala:     x{scale_v:.1f} (ventas), x{scale_r:.1f} (reseñas)")
    return 0


if __name__ == '__main__':
    exit(main())
