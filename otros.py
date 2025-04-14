import sys, subprocess

"""
OTRAS FUNCIONES QUE CORREGIR
"""
def params(file):

    n_servers=2

    #Si se pasa un segundo parámetro, lo usamos
    if len(sys.argv) >= 3:
        try:
            n_servers = int(sys.argv[2])
            if n_servers < 1 or n_servers > 5:
                raise ValueError
        except ValueError:
            print("Error: El número de servidores debe estar entre 1 y 5.")
            #### PONER LOGGINS
            sys.exit(1)
    
    with open(file, "w") as file:
        file.write(str(n_servers))







##LINEA 30 pfinal1.py

"""
#Crear nuevo usuario
    subprocess.run(["newgrp", "lxd"])

    #Importar imagen
    subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias",  IMAGE_DEFAULT])

"""