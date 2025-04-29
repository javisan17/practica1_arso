import subprocess, sys, logging, json
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pfinal.log"),
        logging.StreamHandler()
    ]
)


"""
LXC IMAGE
"""
def create_image():
    """
    Crear una nueva imagen con el alias asignado
    """

    try:
        #Comprobamos si la imagen ya existe
        result = subprocess.run(["lxc", "image", "list", IMAGE_DEFAULT, "--format", "csv"], check=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            #La imagen ya existe, sacamos el fingerprint
            fingerprint = result.stdout.strip().split(",")[0]
            logging.info(f"La imagen {IMAGE_DEFAULT} ya existe ")
            return

        #Si no existe, la importamos
        import_result = subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias", IMAGE_DEFAULT], check=True, capture_output=True, text=True)
        logging.info(f"Imagen {IMAGE_DEFAULT} importada con éxito: {import_result.stdout} ")
        
        #Despues de importar, volvemos a sacer el fingerprint
        result = subprocess.run(["lxc", "image", "list", IMAGE_DEFAULT, "--format", "csv"], check=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            fingerprint = result.stdout.strip().split(",")[0]
            logging.info(f"Fingerprint de la imagen {IMAGE_DEFAULT}: {fingerprint}  ")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al importar la imagen :{e.stderr}  ")
        sys.exit(1)

def delete_image():
    """
    Eliminamos la imagen
    """
    subprocess.run(["lxc","image","delete", IMAGE_DEFAULT])

def create_user():
    """
    Añadir un nuevo usuario para evitar problemas de compatibilidad
    """
    """
    subprocess.run(["newgrp", "lxd"], check=True)
    """
    subprocess.run(["lxd", "init", "--auto"], check=True)


"""
LXC CONTAINERS
"""
def create_container(name):
    """
    Crear un contenedor a partir de una imagen
    """
     #Comprobamos si el contenedor ya existe
    try:
        result = subprocess.run(["lxc","info",name], check=False, capture_output=True,text=True)

        if result.returncode == 0:  #El contedor existe
            logging.info(f"El contenedor {name} ya existe")
             
        #Creamos el nuevo contenedor
        subprocess.run(["lxc", "init", IMAGE_DEFAULT, name], check=True)
        logging.info(f"Contenedor {name} creado con éxito.")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al crear el contenedor {name}: {e.stderr}")
        sys.exit(1)
        


def start_container(name):
    """
    Arrancar un contenedor
    """
     #Comprobamos si el contenedor está arrancado o no
    try:
        result = subprocess.run(["lxc","info",name], check=True, capture_output=True,text=True)
        
        if "Status: RUNNING" in result.stdout:
            logging.info(f"El contenedor {name} ya está en ejecución")   
        elif 'Status: STOPPED' in result.stdout:
            subprocess.run(["lxc", "start", name], check=True)
            logging.info(f"Contenedor {name} iniciado con éxito")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al intentar iniciar el contenedor {name} ")
        logging.error(f"Detalles del error: {e}")

def stop_container(name):
    """
    Parar un contenedor
    """
    
#Comprobamos si el contenedor está parado o no
    try:
        result = subprocess.run(["lxc","info",name, "--format", "json"], check=True, capture_output=True,text=True)
        
        if "Status: STOPPED" in result.stdout:
            logging.info(f"El contenedor {name} ya está parado")   
        elif 'Status: RUNNING'in result.stdout:
            subprocess.run(["lxc", "stop", name], "--force", check=True)
            logging.info(f"Contenedor {name} se ha parado con éxito")   

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al intentar parar el contenedor {name} ")

def delete_container(name):
    """
    Eliminar un contenedor
    """
    
    subprocess.run(["lxc", "delete", name, "--force"], check=True)


"""
LXC Bridges
"""
def create_bridge(bridge_name):
    """
    Crear un bridge
    """
    try:
        # Comprobamos si la red ya existe
        result = subprocess.run(["lxc", "network", "list", "--format", "csv"], check=True, capture_output=True, text=True)
        if bridge_name in result.stdout:
            logging.info(f"La red {bridge_name} ya existe ")
            return

        # Si la red no existe la creamos
        subprocess.run(["lxc", "network", "create", bridge_name], check=True)
        logging.info(f"Red {bridge_name} creada con exito")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al crear la red {bridge_name}: {e.stderr}")
        sys.exit(1)


def config_bridge(bridge_name, ipv4):
    """
    Configurar los bridges
    """

    subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.nat", "true"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.address", ipv4], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.nat", "false"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.address", "none"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "dns.domain", "lxd"], check=True)
    subprocess.run(["lxc", "network", "set", bridge_name, "dns.mode", "none"], check=True)


def attach_network(container, bridge, iface):
    """
    Conectar un contenedor a un bridge en una tarjeta de red (ethx)
    """
    try:
        # Comprobamos si el contenedor ya está conectado a la red
        result = subprocess.run(["lxc","network","list", "--format","json"],capture_output=True,text=True)
        networks = json.loads(result.stdout)

        is_connected = False
        for network in networks:
            if container in network['name']:
                is_connected = True
                break
        if is_connected:
            logging.info(f"El contenedor {container} ya está conectado a la red {bridge}")
            return
        # Si no está conectado, lo conectamos
        subprocess.run(["lxc", "network", "attach", bridge, container, iface], check=True)
        logging.info(f"Contenedor {container} conectado a la red {bridge} usando la interfaz {iface}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al intentar conectar el contenedor {container} a la red {bridge}")


def delete_bridge(bridge):
    """
    Eliminar un bridge
    """

    subprocess.run(["lxc", "network", "delete", bridge])


def config_container(name, iface, ip):
    """
    Configurar un contenedor en una red
    """

    subprocess.run(["lxc", "config", "device", "set", name, iface, "ipv4.address", ip])


"""
FILE
"""
def save_num_servers(n):
    with open(NUM_SERVERS_FILE, "w") as file:
        file.write(str(n))
        logging.info(f"Número de servidores {n} guardado")


def load_num_servers():
    with open(NUM_SERVERS_FILE, "r") as file:
        return int(file.read())
        logging.info(f"Número de servidores recuperado")


"""
LB
"""
def change_netplan_lb():
    """
    Modifica el archivo /etc/netplan/50-cloud-init.yaml en el contendor 'lb'
    """
    """
    try: 
        #Nos aseguramos que el balanceador está arrancado
        start_container(VM_NAMES["balanceador"])
        logging.info(f"Balanceador en marcha")
        
        #Ejecutamos un comando dentro del contenedor 'lb' para modificar el archivo
        #Abrimos el archivo y añadimos las lineas necesarias
        """
        
    #     #El contenido que queremos agregar al archivo
    #   #  netplan_content = """
    #     network:
    #       version: 2
    #       ethernets:
    #         eth0:
    #           dhcp4: true
    #         eth1:
    #           dhcp4: true
        
    #     #Comando para modificar el archivo
    #     command = f"echo '{netplan_content}'| lxc exec lb -- tee /etc/netplan/50-cloud-init.yaml" 
        
    #     #Ejecutamos el comando
    #     subprocess.run(command, shell=True, check=True)

    #     #Reiniciamos el contenedor para aplicar los cambios
    #     subprocess.run(["lxc","restart","lb"], check=True)
    #     logging.info(f"Contenedor lb reiniciado correctamente")
    #     logging.info(f"Archivo /etc/netplan/50-cloud-init.yaml modificado correctamente.")

    #     #Paramos el balanceador
    #     stop_container(VM_NAMES["balanceador"])
    #     logging.info(f"Balanceador parado")

    # except subprocess.CalledProcessError as e:
    #     logging.error(f"Error al modificar el archivo en el contenedor lb: {e.stderr}")
    # """    
    
    config_yaml = """
network:
    version: 2
    ethernets:
        eth0:
            dhcp4: true
        eth1:
            dhcp4: true
    """
    
    # Guardar temporalmente el archivo
    with open("static/files/50-cloud-init.yaml", "w") as file:
        file.write(config_yaml)

    # Copiar al contenedor
    subprocess.run(["lxc", "file", "push", "static/files/50-cloud-init.yaml", "lb/etc/netplan/50-cloud-init.yaml"], check=True)

    # Aplicar configuración dentro del contenedor ?????
    subprocess.run(["lxc", "exec", "lb", "--", "netplan", "apply"], check=True)
    

"""
ORDENES
"""
def create_all(n_servers):
    """
    Crea la red completa (CREATE)
    """
    
    #Crear usuario
    create_user()

    #Crear imagen
    create_image()
    
    
    #Crear bridges lxdbr0 y lxdbr1
    # create_bridge(bridge_name=BRIDGES["LAN1"]) YA ESTÁ CREADA
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
    change_netplan_lb()
    subprocess.run(["lxc","exec",VM_NAMES["balanceador"],"--", "shutdown","-r","now"])
    """
    stop_container(name=VM_NAMES["balanceador"]) 
    """

    #Crear cliente
    create_container(name=VM_NAMES["cliente"])
    attach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["cliente"], iface="eth1", ip="134.3.1.11")

    #Guardar número de servidores
    save_num_servers(n_servers)


def show_console(n_servers):
    """
    Mostrar por consola los contenedores
    """

    contenedores=[VM_NAMES["servidores"][i] for i in range(n_servers)] + [VM_NAMES["cliente"], VM_NAMES["balanceador"]]

    for c in contenedores:
        orden=f"lxc exec {c} bash"
        subprocess.Popen(["xterm", "-e", orden])


def start_all(n_servers):
    """
    Arrancar todos los contenedores
    """

    for i in range(n_servers):
        start_container(VM_NAMES["servidores"][i])
    start_container(VM_NAMES["cliente"])
    start_container(VM_NAMES["balanceador"])


def list_containers():
    """
    Listar los contenedor
    """

    subprocess.run(["lxc", "list"])


def delete_all(n_servers):
    """
    Eliminar todo (VM y conexiones)
    """
    """
    #Paramos todos los servidores
    for i in range(n_servers):
        stop_container(VM_NAMES["servidores"][i])
    stop_container(VM_NAMES["cliente"])
    stop_container(VM_NAMES["balanceador"])
    """
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