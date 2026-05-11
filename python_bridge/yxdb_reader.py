"""
Módulo lector de archivos YXDB (Alteryx Data Format) a Polars DataFrames.

Proporciona funciones para leer archivos YXDB de Alteryx con optimizaciones
de memoria mediante procesamiento por lotes (batch processing), conversión
automática de tipos, y exportación a formatos compatibles con Power BI
(JSON y Arrow IPC).

Ejemplo:
    >>> from yxdb_reader import read_yxdb, df_to_arrow
    >>> df = read_yxdb(r"C:\\ruta\\archivo.yxdb")
    >>> df_to_arrow(df, r"C:\\salida\\archivo.arrow")
"""

import json
import sys
import time
from pathlib import Path

import polars as pl
import pyarrow as pa
from yxdb.yxdb_reader import YxdbReader


# Mapeo de tipos YXDB → Polars
YXDB_TO_POLARS = {
    "Int16": pl.Int16,
    "Int32": pl.Int32,
    "Int64": pl.Int64,
    "Float": pl.Float32,
    "Double": pl.Float64,
    "String": pl.Utf8,
    "WString": pl.Utf8,
    "Bool": pl.Boolean,
    "Date": pl.Date,
    "DateTime": pl.Datetime,
    "Blob": pl.Binary,
    "SpatialObj": pl.Utf8,
}


def map_type(yxdb_type: str) -> pl.DataType:
    """
    Convierte un tipo de dato YXDB a su equivalente en Polars.

    Extrae el nombre del tipo del formato YXDB completo y lo mapea
    al tipo de Polars correspondiente. Si no encuentra coincidencia,
    retorna Utf8 como tipo por defecto.

    Args:
        yxdb_type (str): Nombre del tipo de dato en formato YXDB.
                        Ejemplo: 'Alteryx.System.Types.String'.

    Returns:
        pl.DataType: Tipo de dato de Polars correspondiente.
    """
    return YXDB_TO_POLARS.get(str(yxdb_type).split(".")[-1], pl.Utf8)


def read_yxdb(
    file_path: str,
    batch_size: int = 100_000,
    verbose: bool = True,
) -> pl.DataFrame:
    """
    Lee un archivo YXDB y retorna un DataFrame de Polars optimizado.

    Utiliza procesamiento por lotes para optimizar el uso de memoria
    en archivos grandes. Valida el archivo, detecta esquema, infiere
    tipos automáticamente y muestra información de progreso si se solicita.

    Args:
        file_path (str): Ruta al archivo YXDB a leer.
        batch_size (int): Número de registros por lote. Por defecto 100,000.
        verbose (bool): Si True, imprime información de progreso y schema.
                       Por defecto True.

    Returns:
        pl.DataFrame: DataFrame de Polars con los datos del archivo YXDB
                     con tipos inferenciales automáticos.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta especificada.
        ValueError: Si el archivo no tiene extensión .yxdb.
        Exception: Si hay errores al leer el archivo o procesar datos.

    Example:
        >>> df = read_yxdb("datos.yxdb")
        >>> print(df.shape)
        (10000, 25)
    """
    path = Path(file_path)

    # Validar que el archivo existe
    if not path.exists():
        raise FileNotFoundError(f"[x] Archivo no encontrado: {file_path}")

    # Validar que es un archivo YXDB
    if path.suffix.lower() != ".yxdb":
        raise ValueError(f"[x] El archivo debe ser .yxdb: {file_path}")

    # Calcular tamaño del archivo en MB
    size_mb = path.stat().st_size / (1024 ** 2)

    if verbose:
        print("\n Iniciando lectura...")
        print(f"   Archivo: {path.name}")
        print(f"   Tamaño:  {size_mb:.2f} MB")

    # Iniciar medición de tiempo
    start = time.perf_counter()

    # Abrir archivo YXDB y obtener lista de campos
    reader = YxdbReader(path=str(file_path))
    fields = reader.list_fields()

    # Construir esquema mapeando tipos YXDB → Polars
    schema = {f.name: map_type(f.data_type) for f in fields}

    if verbose:
        print(f"\nSchema detectado ({len(fields)} campos):")
        for f in fields:
            print(
                f"   • {f.name:<30} {str(f.data_type):<15} "
                f"→ {map_type(f.data_type)}"
            )

    # Leer registros en lotes para optimizar uso de RAM
    batches = []
    batch = {col: [] for col in schema}
    row_count = 0

    while reader.next():
        # Leer valores de cada campo en el registro actual
        for f in fields:
            batch[f.name].append(reader.read_name(f.name))
        row_count += 1

        # Procesar lote cuando alcanza el tamaño definido
        if row_count % batch_size == 0:
            # Crear DataFrame sin schema para permitir inferencia automática
            batches.append(pl.DataFrame(batch))
            batch = {col: [] for col in schema}
            if verbose:
                print(f"   ⚡ {row_count:,} filas procesadas...")

    # Procesar último lote si quedan registros
    if any(len(v) > 0 for v in batch.values()):
        batches.append(pl.DataFrame(batch))

    # Manejo de archivo vacío
    if not batches:
        if verbose:
            print("Archivo vacío")
        return pl.DataFrame()

    # Concatenar todos los lotes en un único DataFrame
    df = pl.concat(batches, rechunk=True)
    elapsed = time.perf_counter() - start

    if verbose:
        print("\n[OK] Lectura completada:")
        print(f"   Filas:     {df.height:,}")
        print(f"   Columnas:  {df.width}")
        print(f"   Tiempo:    {elapsed:.2f}s")
        print(f"   Velocidad: {df.height / elapsed:,.0f} filas/seg")
        print(f"   RAM usada: {df.estimated_size('mb'):.2f} MB")
        print("\nPreview (primeras 5 filas):")
        print(df.head(5))

    return df


def df_to_json(df: pl.DataFrame) -> str:
    """
    Serializa un DataFrame de Polars a formato JSON orientado a filas.

    Formato compatible con Power BI y otras herramientas que consumen
    JSON con datos organizados por registro (row-oriented).

    Args:
        df (pl.DataFrame): DataFrame a serializar.

    Returns:
        str: Representación JSON del DataFrame en formato row-oriented.

    Example:
        >>> json_str = df_to_json(df)
        >>> print(json_str[:50])
    """
    # Convertir cada fila a diccionario para obtener formato row-oriented
    # Usar default=str para manejar tipos no serializables como bytes
    records = df.to_dicts()
    return json.dumps(records, default=str)


def df_to_arrow(df: pl.DataFrame, output_path: str) -> None:
    """
    Exporta un DataFrame de Polars a formato Arrow IPC.

    Arrow IPC (Inter-Process Communication) proporciona mejor rendimiento
    para consumo en Power BI en comparación con otros formatos.

    Args:
        df (pl.DataFrame): DataFrame a exportar.
        output_path (str): Ruta de salida para el archivo .arrow.

    Raises:
        IOError: Si hay errores al escribir el archivo.

    Example:
        >>> df_to_arrow(df, r"C:\\salida\\datos.arrow")
         Arrow IPC: C:\\salida\\datos.arrow
    """
    arrow_table = df.to_arrow()
    with pa.ipc.new_file(output_path, arrow_table.schema) as writer:
        writer.write_table(arrow_table)
    print(f"Arrow IPC: {output_path}")


if __name__ == "__main__":
    # Validar argumentos de línea de comandos
    if len(sys.argv) < 2:
        print(
            json.dumps({
                "status": "error",
                "message": "Uso: python yxdb_reader.py <archivo.yxdb>",
            })
        )
        sys.exit(1)

    try:
        # Leer archivo YXDB
        df = read_yxdb(sys.argv[1])

        # Retornar resultado en JSON con información del DataFrame
        print(
            json.dumps({
                "status": "success",
                "rows": df.height,
                "cols": df.width,
                "columns": df.columns,
            }, default=str)
        )

    except Exception as e:
        # Retornar error en formato JSON
        print(
            json.dumps({
                "status": "error",
                "message": str(e),
            })
        )
        sys.exit(1)