import sys, subprocess

"""
OTRAS FUNCIONES QUE CORREGIR
"""

##LINEA 30 pfinal1.py

"""
#Crear nuevo usuario
    subprocess.run(["newgrp", "lxd"])

    #Importar imagen
    subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias",  IMAGE_DEFAULT])

"""


def create_user():
    """
    Añadir un nuevo usuario para evitar problemas de compatibilidad
    ESTO SE DEBE CREAR EN CONSOLA, DA MUCHOS ERRORES
    """

    subprocess.run(["newgrp", "lxd"], check=True)
    subprocess.run(["lxd", "init", "--auto"], check=True)