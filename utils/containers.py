import subprocess
from consts import IMAGE_DEFAULT
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC CONTAINERS
"""


def create_container(name):
    """
    Crear un contenedor a partir de una imagen
    """

    subprocess.run(["lxc", "init", IMAGE_DEFAULT, name], check=True)
    logger.info(f"Contenedor {name} creado con éxito.")

    ###CREAR VACIO DA PROBLEMAS
    #subprocess.run(["lxc", "config", "device", "remove", "name", "eth0"], check=True)


def start_container(name):
    """
    Arrancar un contenedor
    """
    
    subprocess.run(["lxc", "start", name], check=True)
    logger.info(f"Contenedor iniciado: {name}")


def stop_container(name):
    """
    Detener un contenedor
    """
    
    subprocess.run(["lxc", "stop", name], check=True)
    logger.info(f"Contenedor parado: {name}")


def delete_container(name):
    """
    Eliminar un contenedor
    """
    
    subprocess.run(["lxc", "delete", name, "--force"], check=True)
    logger.info(f"Contenedor eliminado: {name}")


def config_container(name, iface, ip):
    """
    Configurar un contenedor en una red
    """

    subprocess.run(["lxc", "config", "device", "set", name, iface, "ipv4.address", ip])
    logger.info(f"Contenedor {name} conectado a {iface} con ip {ip} ")