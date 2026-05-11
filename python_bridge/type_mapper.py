"""
Módulo de mapeo de tipos de datos YXDB a Polars.

Este módulo proporciona funciones para convertir tipos de datos nativos
de Alteryx (YXDB) a sus equivalentes en la librería Polars, facilitando
la lectura y procesamiento de datos YXDB en formato Polars.
"""
import polars as pl
# Diccionario de mapeo: tipos YXDB → tipos Polars
YXDB_TO_POLARS = {
    "Int16": pl.Int16,
    "Int32": pl.Int32,
    "Int64": pl.Int64,
    "Float": pl.Float32,
    "Float64": pl.Float64,
    "Double": pl.Float64,
    "String": pl.Utf8,
    "WString": pl.Utf8,
    "Bool": pl.Boolean,
    "Date": pl.Date,
    "DateTime": pl.Datetime,
    "Blob": pl.Binary,
    "SpatialObj": pl.Utf8,
}


def map_field_type(yxdb_type: str) -> type:
    """
    Convierte un tipo de dato YXDB a su equivalente en Polars.

    Args:
        yxdb_type (str): Nombre del tipo de dato en formato YXDB.

    Returns:
        type: Tipo de dato de Polars correspondiente.
              Por defecto retorna pl.Utf8 si el tipo no está mapeado.
    """
    return YXDB_TO_POLARS.get(yxdb_type, pl.Utf8)


def get_schema(fields) -> dict:
    """
    Genera un esquema de Polars a partir de los campos de un archivo YXDB.

    Args:
        fields: Iterable de objetos field que contienen 'name' y 'field_type'.

    Returns:
        dict: Diccionario donde las claves son nombres de campos
              y los valores son tipos de datos de Polars.
    """
    return {
        field.name: map_field_type(str(field.field_type))
        for field in fields
    }


def print_schema(fields) -> None:
    """
    Imprime el esquema detectado en un formato legible.

    Muestra una comparación entre tipos YXDB originales y sus
    equivalentes en Polars para facilitar la verificación.

    Args:
        fields: Iterable de objetos field que contienen 'name' y 'field_type'.
    """
    print("\nSchema detectado:")
    for field in fields:
        # Obtener el tipo de Polars equivalente al tipo YXDB
        polars_type = map_field_type(str(field.field_type))
        print(
            f"   {field.name:<30} {str(field.field_type):<15} "
            f"→ {polars_type}"
        )