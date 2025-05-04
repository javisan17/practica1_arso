import subprocess
from logger import setup_logger, get_logger
from consts import VM_NAMES



"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
CONSOLE
"""


def show_consoles(n_servers):
    """
    Mostrar por consola los contenedores
    """

    contenedores=[VM_NAMES["servidores"][i] for i in range(n_servers)] + [VM_NAMES["cliente"], VM_NAMES["balanceador"]]

    for c in contenedores:
        orden=f"lxc exec {c} bash"
        subprocess.Popen(["xterm", "-e", orden])
        logger.info(f"Consola del contenedor {c} abierta correctamente")


def show_console(name):
    """
    Abrir la consola del contenedor dicho
    """

    orden=f"lxc exec {name} bash"
    subprocess.Popen(["xterm", "-e", orden])

    logger.info(f"Consola del contenedor {name} abierta correctamente")


###ES UN POCO IRRELAVANTES PORQUE CUANDO SE PARAN LOS SERVIDORES LAS CONSOLAS SE CIERRAN AUTOMATICAMENTE
def close_consoles(n_servers):
    """
    Cerrar las consolas de los contenedores
    """

    subprocess.run(["pkill", "xterm"])
    logger.info("Consolas cerradas correctamente")