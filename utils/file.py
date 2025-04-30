from consts import NUM_SERVERS_FILE
from logger import setup_logger, get_logger

"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
FILE
"""


def save_num_servers(n):
    with open(NUM_SERVERS_FILE, "w") as file:
        file.write(str(n))
    logger.info(f"Número de servidores {n} guardados correctamente")


def load_num_servers():
    with open(NUM_SERVERS_FILE, "r") as file:
        return int(file.read())

