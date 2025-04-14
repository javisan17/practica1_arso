import sys, subprocess
from consts import VALID_ORDERS, DEFAULT_NUM_SERVERS, MIN_SERVERS, MAX_SERVERS
from ordenes import crear_red, params



"""
Configurar logs
"""



"""
Iniciar sesiones e imágenes
"""

#Crear nuevo usuario
subprocess.run(["newgrp", "lxc"])

#Importar imagen
subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias",  "ubuntu2004"])









orden=sys.argv[1]

#CREATE




