import subprocess
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES, MAX_SERVERS, MIN_SERVERS, IP_CL, IP_S
from logger import setup_logger, get_logger
from utils.containers import create_container, start_container, stop_container, delete_container, config_container
from utils.image import create_image, delete_image
from utils.bridges import create_bridge, config_bridge, attach_network, delete_bridge
from utils.file import save_num_servers
from utils.balanceador import change_netplan


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
ORDENES
"""


def create_all(n_servers):
    """
    Crea la infraesctrutura de la red completa (CREATE)
    """

    logger.info(f"Iniciando creación de infraestructura con {n_servers} servidores")

    #Crear imagen
    create_image()

    #Crear bridges lxdbr0 y lxdbr1
    #create_bridge(bridge_name=BRIDGES["LAN1"])
    config_bridge(bridge_name=BRIDGES["LAN1"], ipv4=BRIDGES_IPV4["lxdbr0"])
    create_bridge(bridge_name=BRIDGES["LAN2"])
    config_bridge(bridge_name=BRIDGES["LAN2"], ipv4=BRIDGES_IPV4["lxdbr1"])

    #Crear servidores
    for i in range(n_servers):
        create_container(name=VM_NAMES["servidores"][i])
        attach_network(container=VM_NAMES["servidores"][i], bridge=BRIDGES["LAN1"], iface="eth0")
        config_container(name=VM_NAMES["servidores"][i], iface="eth0", ip=IP_S[f"s{i+1}"])

    #Guardar número de servidores
    save_num_servers(n_servers)
    logger.info("Número de servidores guardados correctamente")
    
    #Crear balanceador
    create_container(name=VM_NAMES["balanceador"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN1"], iface="eth0")
    config_container(name=VM_NAMES["balanceador"], iface="eth0", ip=IP_LB["eth0"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["balanceador"], iface="eth1", ip=IP_LB["eth1"])

    #Cambiar el archivo 50-cloud-init.yaml para tener las dos subredes
    start_container(name=VM_NAMES["balanceador"])
    change_netplan(name=VM_NAMES["balanceador"])
    stop_container(name=VM_NAMES["balanceador"]) 

    #Crear cliente
    create_container(name=VM_NAMES["cliente"])
    attach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["cliente"], iface="eth1", ip=IP_CL)

    #Cambiar el archivo 50-cloud-init.yaml para tener la subred adecuada
    start_container(name=VM_NAMES["cliente"])
    change_netplan(name=VM_NAMES["cliente"])
    stop_container(name=VM_NAMES["cliente"])

    logger.info("Infraestructura creada correctamente.")


def start_all(n_servers):
    """
    Arrancar todos los contenedores
    """

    for i in range(n_servers):
        start_container(VM_NAMES["servidores"][i])
    start_container(VM_NAMES["cliente"])
    start_container(VM_NAMES["balanceador"])
    logger.info("Todos los contenedores han sido iniciados correctamente")


def list_containers():
    """
    Listar los contenedor
    """

    logger.info("Listando contenedores")
    subprocess.run(["lxc", "list"])


def delete_all(n_servers):
    """
    Eliminar todo (VM y conexiones)
    """

    logger.info("Eliminando toda la infraestructura")

    #Eliminar imagen
    delete_image()

    #Eliminar contenedores
    for i in range(n_servers):
        delete_container(name=VM_NAMES["servidores"][i])
    delete_container(name=VM_NAMES["cliente"])
    delete_container(name=VM_NAMES["balanceador"])

    #Eliminar conexiones (bridges). Se opta por no eliminar el bridge lxdbr0 por ser el bridge creado por el profile default
    delete_bridge(bridge=BRIDGES["LAN2"])

    logger.info("Eliminación completada.")