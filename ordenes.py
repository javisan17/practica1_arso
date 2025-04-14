import subprocess, sys
from consts import VM_NAMES,NUM_SERVERS_FILE, BRIDGES_IPV4, IP_LB, BRIDGES


"""
LXC CONTAINERS
"""
def create_container(name, image):
    """
    Crear un contenedor a partir de una imagen
    """

    subprocess.run(["lxc", "init", image, name], check=True)


def start_container(name):
    """
    Arrancar un contenedor
    """
    
    subprocess.run(["lxc", "start", name], check=True)


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
    with open("50-cloud-init.yaml", "w") as file:
        file.write(config_yaml)

    # Copiar al contenedor
    subprocess.run(["lxc", "file", "push", "50-cloud-init.yaml", "lb/etc/netplan/50-cloud-init.yaml"], check=True)

    # Aplicar configuración dentro del contenedor ?????
    subprocess.run(["lxc", "exec", "lb", "--", "netplan", "apply"], check=True)


"""
ORDENES
"""
def create_all(n_servers, image):
    """
    Crea la red completa (CREATE)
    """

    #Crear bridges lxdbr0 y lxdbr1
    create_bridge(bridge_name=BRIDGES["LAN1"])
    config_bridge(bridge_name=BRIDGES["LAN1"], ipv4=BRIDGES_IPV4["lxdbr0"])
    create_bridge(bridge_name=BRIDGES["LAN2"])
    config_bridge(bridge_name=BRIDGES["LAN2"], ipv4=BRIDGES_IPV4["lxdbr1"])

    #Crear servidores
    for i in range(n_servers):
        create_container(name=VM_NAMES["servidores"][i], image=image)
        config_container(name=VM_NAMES["servidores"][i], iface="eth0", ip=f"134.3.0.1{i}")
        attach_network(container=VM_NAMES["servidores"][i], bridge=BRIDGES["LAN1"], iface="eth0")
    
    #Crear balanceador
    create_container(name=VM_NAMES["balanceador"], image=image)
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN1"], iface="eth0")
    config_container(name=VM_NAMES["balanceador"], iface="eth0", ip=IP_LB["eth0"])
    attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["balanceador"], iface="eth1", ip=IP_LB["eth1"])
    change_netplan_lb()

    #Crear cliente
    create_container(name=VM_NAMES["cliente"], image=image)
    attach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN2"], iface="eth1")
    config_container(name=VM_NAMES["cliente"], iface="eth1", ip="134.3.1.11")

    #Guardar número de servidores
    save_num_servers(n_servers)


def show_console(n_servers):
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