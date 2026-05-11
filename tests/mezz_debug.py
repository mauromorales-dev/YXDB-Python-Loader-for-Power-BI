"""Diagnóstico del archivo .mez y de la estructura del conector.

Este script valida que el paquete .mez exista, revisa su contenido, verifica
la carpeta de `python_bridge` y lista los recursos del proyecto para ayudar a
detectar problemas de empaquetado o instalación.
"""

import zipfile
import os
from pathlib import Path

MEZ_PATH = "bin/YxdbConnector.mez"
PBI_PATH = r"C:\Users\DELL\Documents\Power BI Desktop\Custom Connectors\YxdbConnector.mez"


def main() -> None:
    """Ejecuta el diagnóstico del conector YXDB.

    Imprime el estado del archivo .mez local y del archivo instalado en
    Power BI, además de listar el contenido del paquete y los archivos de
    soporte del proyecto.
    """
    print("=" * 60)
    print(" DIAGNÓSTICO DEL CONECTOR YXDB")
    print("=" * 60)

    # Verificar archivo .mez en bin/
    print("\n 1. Archivo .mez en bin/")
    if os.path.exists(MEZ_PATH):
        size = Path(MEZ_PATH).stat().st_size / 1024
        print(f"   [OK] Encontrado — {size:.1f} KB")
    else:
        print(f"   [X] NO encontrado en: {MEZ_PATH}")

    # Verificar archivo .mez en Power BI
    print("\n 2. Archivo .mez en Power BI Custom Connectors")
    if os.path.exists(PBI_PATH):
        size = Path(PBI_PATH).stat().st_size / 1024
        print(f"   [OK] Encontrado — {size:.1f} KB")
    else:
        print(f"   [X] NO encontrado en: {PBI_PATH}")

    # Contenido del .mez
    print("\n 3. Archivos dentro del .mez:")
    try:
        with zipfile.ZipFile(MEZ_PATH, 'r') as z:
            for f in z.namelist():
                info = z.getinfo(f)
                print(f"   • {f:<30} {info.file_size} bytes")
    except Exception as e:
        print(f"   [X] Error leyendo .mez: {e}")

    # Contenido del archivo .m principal
    print("\n 4. Contenido de YxdbConnector.m:")
    try:
        with zipfile.ZipFile(MEZ_PATH, 'r') as z:
            content = z.read('YxdbConnector.m').decode('utf-8')
            print(content)
    except KeyError:
        print("   [X] YxdbConnector.m NO encontrado dentro del .mez")
        print("   Archivos disponibles:")
        with zipfile.ZipFile(MEZ_PATH, 'r') as z:
            for f in z.namelist():
                print(f"   • {f}")
    except Exception as e:
        print(f"   [X] Error: {e}")

    # Verificar python_bridge
    print("\n 5. Archivos en python_bridge/:")
    bridge_path = "python_bridge"
    if os.path.exists(bridge_path):
        for f in os.listdir(bridge_path):
            print(f"   • {f}")
    else:
        print(f"   [X] Carpeta no encontrada: {bridge_path}")

    # Verificar resources/
    print("\n 6. Archivos en resources/:")
    resources_path = "resources"
    if os.path.exists(resources_path):
        for f in os.listdir(resources_path):
            print(f"   • {f}")
    else:
        print(f"   [X] Carpeta no encontrada: {resources_path}")

    print("\n" + "=" * 60)
    print(" Copia este output completo y compártelo")
    print("=" * 60)


# Punto de entrada del script.
if __name__ == "__main__":
    main()