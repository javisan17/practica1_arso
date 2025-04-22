import subprocess, sys
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES


"""
LXC IMAGE
"""
def create_image():
    """
    Crear una nueva imagen con el alias asignado
    """

    subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias", IMAGE_DEFAULT], check=True)


def create_user():
    """
    Añadir un nuevo usuario para evitar problemas de compatibilidad
    """

    subprocess.run(["newgrp", "lxd"], check=True)
    subprocess.run(["lxd", "init", "--auto"], check=True)


"""
LXC CONTAINERS
"""
def create_container(name):
    """
    Crear un contenedor a partir de una imagen
    """

    subprocess.run(["lxc", "init", IMAGE_DEFAULT, name], check=True)


def start_container(name):
    """
    Arrancar un contenedor
    """
    
    subprocess.run(["lxc", "start", name], check=True)


def stop_container(name):
    """
    Parar un contenedor
    """
    
    subprocess.run(["lxc", "stop", name], check=True)


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

    subprocess.run(["lxc", "network", "create", bridge_name], check=True)


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

    subprocess.run(["lxc", "network", "attach", bridge, container, iface], check=True)


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


def load_num_servers():
    with open(NUM_SERVERS_FILE, "r") as file:
        return int(file.read())


"""
LB
"""
def change_netplan_lb():
    """
    Modifica el archivo /etc/netplan/50-cloud-init.yaml
    """

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
        config_container(name=VM_NAMES["servidores"][i], iface="eth0", ip=f"134.3.0.1{i}")
        attach_network(container=VM_NAMES["servidores"][i], bridge=BRIDGES["LAN1"], iface="eth0")
    
    #Crear balanceador
    create_container(name=VM_NAMES["balanceador"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN1"], iface="eth0")
    config_container(name=VM_NAMES["balanceador"], iface="eth0", ip=IP_LB["eth0"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["balanceador"], iface="eth1", ip=IP_LB["eth1"])

    ### MUCHOS PROBLEMAS CON CAMBIAR ESTE ARCHIVO (probar --mode=0644)
    start_container(name=VM_NAMES["balanceador"])
    change_netplan_lb()
    stop_container(name=VM_NAMES["balanceador"]) 

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

    #Eliminar contenedores
    for i in range(n_servers):
        delete_container(name=VM_NAMES["servidores"][i])
    delete_container(name=VM_NAMES["cliente"])
    delete_container(name=VM_NAMES["balanceador"])

    #Eliminar conexiones (bridges)
    for bridge in BRIDGES.values():
        delete_bridge(bridge=bridge)