import subprocess
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC Bridges
"""


def create_bridge(bridge_name):
    """
    Crear un bridge
    """

    subprocess.run(["lxc", "network", "create", bridge_name], check=True)
    logger.info(f"Bridge creado: {bridge_name}")


def config_bridge(bridge_name, ipv4):
    """
    Configurar los bridges
    """

    subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.nat", "true"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.address", ipv4], check=True)
    logger.info(f"{ipv4} asignada correctamente al bridge: {bridge_name}")
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.nat", "false"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.address", "none"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "dns.domain", "lxd"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "dns.mode", "none"], check=True)
    logger.info(f"Bridge configurado correctamente: {bridge_name}")


def attach_network(container, bridge, iface):
    """
    Conectar un contenedor a un bridge en una tarjeta de red (ethx)
    """

    subprocess.run(["lxc", "network", "attach", bridge, container, iface], check=True)
    logger.info(f"Conectando {container} al bridge {bridge} por {iface}")


# NO SE PUEDE DETACHEAR DA ERROR DE PERFIL. AL HEREDAR NO DEJA DETACHEAR
# def detach_network(container, bridge, iface):
#     """
#     Conectar un contenedor a un bridge en una tarjeta de red (ethx)
#     """

#     subprocess.run(["lxc", "network", "detach", bridge, container, iface], check=True)


def delete_bridge(bridge):
    """
    Eliminar un bridge
    """

    subprocess.run(["lxc", "network", "delete", bridge])
    logger.info(f"Bridge eliminado: {bridge}")