import subprocess
from consts import IMAGE_DEFAULT
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC IMAGE
"""


def create_image():
    """
    Crear una nueva imagen con el alias asignado
    """

    subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias", IMAGE_DEFAULT], check=True)
    logger.info(f"Imagen {IMAGE_DEFAULT} importada con éxito.")



def delete_image():
    """
    Eliminar imagen creada de ubuntu
    """

    subprocess.run(["lxc", "image", "delete", IMAGE_DEFAULT])
    logger.info("Imagen local eliminada con éxito.")

