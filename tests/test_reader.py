"""Pruebas funcionales para la lectura y exportación de archivos YXDB.

Este módulo valida la lectura básica, la serialización a JSON, la generación
de Parquet en streaming y la compatibilidad con LazyFrame de Polars.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python_bridge"))

from yxdb_reader import read_yxdb, df_to_json
from streaming_reader import stream_yxdb_to_parquet, read_parquet_lazy
import polars as pl
import json
import time

# Ruta al archivo de prueba.
YXDB_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "CO Store File - North.yxdb"
)

def test_archivo_existe():
    """Comprueba que el archivo de prueba exista en disco."""
    assert os.path.exists(YXDB_FILE), f"[X] Archivo no encontrado: {YXDB_FILE}"
    print("[ok] test_archivo_existe")

def test_lectura_basica():
    """Verifica que la lectura básica retorne un DataFrame válido."""
    df = read_yxdb(YXDB_FILE, verbose=False)
    assert isinstance(df, pl.DataFrame), "[X] No retornó DataFrame"
    assert df.height > 0,                "[X] DataFrame vacío"
    assert df.width > 0,                 "[X] Sin columnas"
    print(f"[ok] test_lectura_basica — {df.height} filas x {df.width} cols")

def test_tipos_no_nulos():
    """Verifica que todas las columnas tengan un tipo inferido."""
    df = read_yxdb(YXDB_FILE, verbose=False)
    for col, dtype in zip(df.columns, df.dtypes):
        assert dtype is not None, f"[X] Columna {col} sin tipo"
    print(f"[ok] test_tipos_no_nulos — {df.width} columnas con tipos correctos")

def test_schema_consistente():
    """Verifica que el esquema del DataFrame sea consistente."""
    df = read_yxdb(YXDB_FILE, verbose=False)
    assert len(df.columns) == df.width
    assert len(df.dtypes)  == df.width
    print("[ok] test_schema_consistente")

def test_df_to_json():
    """Comprueba que el DataFrame se serialice correctamente a JSON."""
    df   = read_yxdb(YXDB_FILE, verbose=False)
    js   = df_to_json(df)
    data = json.loads(js)
    assert isinstance(data, list),     "[X] JSON no es lista"
    assert len(data) == df.height,     "[X] Filas no coinciden"
    assert len(data[0]) == df.width,   "[X] Columnas no coinciden"
    print(f"[ok] test_df_to_json — {len(data)} registros serializados")

def test_streaming_parquet():
    """Verifica que la exportación por streaming genere un Parquet válido."""
    output = YXDB_FILE.replace(".yxdb", "_test.parquet")
    path   = stream_yxdb_to_parquet(YXDB_FILE, output, verbose=False)
    assert os.path.exists(path), "[X] Parquet no fue creado"
    df = pl.read_parquet(path)
    assert df.height > 0,        "[X] Parquet vacío"
    print(f"[ok] test_streaming_parquet — {df.height} filas en Parquet")
    os.remove(path)  # limpiar archivo de prueba

def test_lazy_parquet():
    """Comprueba que el Parquet pueda leerse como LazyFrame."""
    output = YXDB_FILE.replace(".yxdb", "_lazy_test.parquet")
    stream_yxdb_to_parquet(YXDB_FILE, output, verbose=False)
    lf = read_parquet_lazy(output)
    assert isinstance(lf, pl.LazyFrame), "[X] No retornó LazyFrame"
    df = lf.collect()
    assert df.height > 0,                "[X] LazyFrame vacío"
    print(f"[ok] test_lazy_parquet — {df.height} filas con LazyFrame")
    os.remove(output)

def test_velocidad():
    """Mide la velocidad de lectura del archivo YXDB."""
    start   = time.perf_counter()
    df      = read_yxdb(YXDB_FILE, verbose=False)
    elapsed = time.perf_counter() - start
    vel     = df.height / elapsed if elapsed > 0 else float("inf")
    print(f"[ok] test_velocidad — {vel:,.0f} filas/seg en {elapsed:.3f}s")

# Punto de entrada para ejecutar las pruebas desde la terminal.
if __name__ == "__main__":
    tests = [
        test_archivo_existe,
        test_lectura_basica,
        test_tipos_no_nulos,
        test_schema_consistente,
        test_df_to_json,
        test_streaming_parquet,
        test_lazy_parquet,
        test_velocidad,
    ]

    print("=" * 50)
    print("Corriendo tests...")
    print("=" * 50)

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[X] {test.__name__} FALLÓ: {e}")
            failed += 1

    print("=" * 50)
    print(f"Resultado: {passed} passed — {failed} failed")
    if failed == 0:
        print(" ¡Todos los tests pasaron!")
    print("=" * 50)