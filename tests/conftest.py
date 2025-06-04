import os
import sys

# Añadir el directorio raíz del proyecto al sys.path para que 'import app' funcione en los tests
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
