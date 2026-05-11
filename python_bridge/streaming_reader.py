"""Conversión por streaming de YXDB a Parquet para archivos grandes.

Este módulo lee registros YXDB por bloques y los escribe en Parquet para
que puedan consumirse de forma eficiente desde Power BI.
"""

from yxdb.yxdb_reader import YxdbReader
import polars as pl
import pyarrow.parquet as pq
import json
import sys
import time
from pathlib import Path
from yxdb_reader import map_type


def _normalize_chunk(chunk: dict, schema: dict) -> dict:
    """Normaliza los valores del bloque antes de crear el DataFrame.

    Polars puede fallar cuando una columna declarada como texto recibe
    valores numéricos mezclados. Esta función convierte solo las columnas
    Utf8 a texto y conserva los valores None.

    Args:
        chunk (dict): Datos de columnas acumulados para el bloque actual.
        schema (dict): Esquema de Polars indexado por nombre de columna.

    Returns:
        dict: Bloque normalizado listo para pasarse a Polars.
    """
    normalized = {}

    for column_name, values in chunk.items():
        column_type = schema[column_name]

        if column_type == pl.Utf8:
            normalized[column_name] = [
                None if value is None else str(value)
                for value in values
            ]
        else:
            normalized[column_name] = values

    return normalized


def stream_yxdb_to_parquet(file_path: str,
                            output_path: str = None,
                            chunk_size: int = 500_000,
                            verbose: bool = True) -> str:
    """Convierte un archivo YXDB a Parquet por bloques.

    Esto evita cargar todo el conjunto de datos en memoria y resulta más
    adecuado para archivos grandes consumidos por Power BI.

    Args:
        file_path (str): Ruta del archivo YXDB de origen.
        output_path (str, optional): Ruta del archivo Parquet de salida.
        chunk_size (int): Número de filas a acumular antes de escribir.
        verbose (bool): Indica si se imprime información de progreso.

    Returns:
        str: Ruta del archivo Parquet generado.

    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    # Ruta de salida automática si no se especifica
    if output_path is None:
        output_path = str(path.with_suffix(".parquet"))

    size_mb = path.stat().st_size / (1024 ** 2)

    if verbose:
        print("\nStreaming YXDB → Parquet")
        print(f"   Archivo:    {path.name}")
        print(f"   Tamaño:     {size_mb:.2f} MB")
        print(f"   Chunk size: {chunk_size:,} filas")
        print(f"   Output:     {output_path}")

    start = time.perf_counter()

    reader     = YxdbReader(path=str(file_path))
    fields     = reader.list_fields()
    schema     = {f.name: map_type(f.data_type) for f in fields}
    pl_schema  = pl.DataFrame(schema=schema).to_arrow().schema

    writer      = None
    chunk       = {col: [] for col in schema}
    total_rows  = 0
    chunk_count = 0

    while reader.next():
        for f in fields:
            chunk[f.name].append(reader.read_name(f.name))
        total_rows += 1

        if total_rows % chunk_size == 0:
            chunk_count += 1
            df    = pl.DataFrame(_normalize_chunk(chunk, schema), schema=schema)
            table = df.to_arrow()

            if writer is None:
                writer = pq.ParquetWriter(
                    output_path,
                    pl_schema,
                    compression="snappy"
                )
            writer.write_table(table)

            if verbose:
                print("Chunk {chunk_count} — {total_rows:,} filas escritas...")

                # Libera RAM inmediatamente
            chunk = {col: [] for col in schema}
            del df, table

            # Escribe el último bloque pendiente
    if any(len(v) > 0 for v in chunk.values()):
        df    = pl.DataFrame(_normalize_chunk(chunk, schema), schema=schema)
        table = df.to_arrow()
        if writer is None:
            writer = pq.ParquetWriter(
                output_path,
                pl_schema,
                compression="snappy"
            )
        writer.write_table(table)

    if writer:
        writer.close()

    elapsed     = time.perf_counter() - start
    out_size_mb = Path(output_path).stat().st_size / (1024 ** 2)

    if verbose:
        print("\nParquet generado:")
        print(f"   Total filas:  {total_rows:,}")
        print(f"   Tiempo:       {elapsed:.2f}s")
        print(f"   Velocidad:    {total_rows/elapsed:,.0f} filas/seg")
        print(f"   Tamaño input: {size_mb:.2f} MB")
        print(f"   Tamaño output:{out_size_mb:.2f} MB")
        compresion = ((size_mb - out_size_mb) / size_mb) * 100
        print(f"   Compresión:   {compresion:.1f}%")

    return output_path


def read_parquet_lazy(parquet_path: str) -> pl.LazyFrame:
    """Lee un archivo Parquet como un LazyFrame de Polars.

    Args:
        parquet_path (str): Ruta del archivo Parquet.

    Returns:
        pl.LazyFrame: Escaneo perezoso del archivo Parquet.
    """
    return pl.scan_parquet(parquet_path)


# Punto de entrada del script para ejecutar la conversión desde la terminal.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status":  "error",
            "message": "Uso: python streaming_reader.py <archivo.yxdb> [output.parquet]"
        }))
        sys.exit(1)

    file_path   = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        parquet_path = stream_yxdb_to_parquet(file_path, output_path)
        print(json.dumps({
            "status":       "success",
            "parquet_path": parquet_path
        }))
    except Exception as e:
        print(json.dumps({
            "status":  "error",
            "message": str(e)
        }))
        sys.exit(1)