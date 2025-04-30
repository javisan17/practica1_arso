import subprocess
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES, MAX_SERVERS, MIN_SERVERS
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
    create_bridge(bridge_name=BRIDGES["LAN1"])
    config_bridge(bridge_name=BRIDGES["LAN1"], ipv4=BRIDGES_IPV4["lxdbr0"])
    create_bridge(bridge_name=BRIDGES["LAN2"])
    config_bridge(bridge_name=BRIDGES["LAN2"], ipv4=BRIDGES_IPV4["lxdbr1"])

    #Crear servidores
    for i in range(n_servers):
        create_container(name=VM_NAMES["servidores"][i])
        attach_network(container=VM_NAMES["servidores"][i], bridge=BRIDGES["LAN1"], iface="eth0")
        config_container(name=VM_NAMES["servidores"][i], iface="eth0", ip=f"134.3.0.1{i+1}")
    
    #Crear balanceador
    create_container(name=VM_NAMES["balanceador"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN1"], iface="eth0")
    config_container(name=VM_NAMES["balanceador"], iface="eth0", ip=IP_LB["eth0"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["balanceador"], iface="eth1", ip=IP_LB["eth1"])

    ### MUCHOS PROBLEMAS CON CAMBIAR ESTE ARCHIVO (probar --mode=0644)
    start_container(name=VM_NAMES["balanceador"])
    change_netplan(name=VM_NAMES["balanceador"])
   # subprocess.run(["lxc", "exec", "lb", "--", "shutdown", "-r", "now"])
    stop_container(name=VM_NAMES["balanceador"]) 

    #Crear cliente
    create_container(name=VM_NAMES["cliente"])
   # detach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN1"], iface="eth0")
    attach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["cliente"], iface="eth1", ip="134.3.1.11")
    start_container(name=VM_NAMES["cliente"])
    change_netplan(name=VM_NAMES["cliente"])
    stop_container(name=VM_NAMES["cliente"])


    #Guardar número de servidores
    save_num_servers(n_servers)

    logger.info("Infraestructura creada correctamente.")


def show_console(n_servers):
    """
    Mostrar por consola los contenedores
    """

    contenedores=[VM_NAMES["servidores"][i] for i in range(n_servers)] + [VM_NAMES["cliente"], VM_NAMES["balanceador"]]

    for c in contenedores:
        orden=f"lxc exec {c} bash"
        subprocess.Popen(["xterm", "-e", orden])
        logger.info(f"Consola del contenedor {c} abierta correctamente")


def start_all(n_servers):
    """
    Arrancar todos los contenedores
    """

    for i in range(n_servers):
        start_container(VM_NAMES["servidores"][i])
    start_container(VM_NAMES["cliente"])
    start_container(VM_NAMES["balanceador"])
    logger.info("Todos los contenedores han sido iniciados")


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

    #Eliminar conexiones (bridges)
    for bridge in BRIDGES.values():
        delete_bridge(bridge=bridge)

    logger.info("Eliminación completada.")


"""
Ordenes opcionales
"""

def create_server ():
    """
    Crear el siguiente servidor disponible entre s1 y s5.
    """

    logger.info("Buscando servidor libre para crear...")

    for i in range(MAX_SERVERS):
        name = VM_NAMES["servidores"][i]
        result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
        if "not found" in result.stderr:
            logger.info(f"Creando nuevo servidor disponible: {name}")
            create_container(name=name)
            attach_network(container=name, bridge=BRIDGES["LAN1"], iface="eth0")
            ip=f"134.3.0.1{i+1}"
            config_container(name=name, iface="eth0", ip=ip)
            logger.info(f"Servidor {name} creado correctamente con IP {ip} ")
            return

    logger.warning(f"Ya existen {MAX_SERVERS}  servidores. No se puede crear más.")

def delete_last_server():
    """
    Eliminar el ultimo servidor disponible entre s1 y s5.
    """

    logger.info("Buscando último servidor para eliminar...")

    for i in reversed(range(MAX_SERVERS)):
        name = VM_NAMES["servidores"][i]
        result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
        if "not found" not in result.stderr:
            logger.info(f"Eliminando servidor: {name}")
            delete_container(name=name)
            logger.info(f"Servidor {name} eliminado correctamente.")
            return

    logger.warning("No hay servidores creados. No se puede eliminar ninguno.")


def start_server(name):
    """
    Arrancar el servidor de nombre que se pase por parámetro
    """

    logger.info(f"Solicitado arrancar servidor: {name}")

    #Verificar que el nombre está en la lista permitida
    if name not in VM_NAMES["servidores"]:
        logger.error(f"Nombre de servidor inválido: {name}")
        return

    #Verificar si el contenedor existe
    result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    if "not found" in result.stderr:
        logger.warning(f"El contenedor {name} no existe.")
        return

    #Verificar si está corriendo
    if "Status: RUNNING" in result.stdout:
        logger.info(f"Servidor {name} ya está corriendo.")
    else:
        start_container(name=name)
        logger.info(f"Servidor {name} corriendo correctamente.")


def stop_server(name):
    """
    Detener el servidor de nombre que se pase por parámetro
    """

    logger.info(f"Solicitado parar servidor: {name}")

    #Verificar que el nombre está en la lista permitida
    if name not in VM_NAMES["servidores"]:
        logger.error(f"Nombre de servidor inválido: {name}")
        return

    #Verificar si el contenedor existe
    result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    if "not found" in result.stderr:
        logger.warning(f"El contenedor {name} no existe.")
        return

    #Verificar si está corriendo
    if "Status: RUNNING" in result.stdout:
        stop_container(name)
        logger.info(f"Servidor {name} detenido correctamente.")
    else:
        logger.info(f"Servidor {name} ya estaba detenido.")