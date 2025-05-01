import subprocess
from logger import setup_logger, get_logger
from consts import VM_NAMES


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


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
    #Guardar temporalmente el archivo
    with open("static/files/50-cloud-init.yaml", "w") as file:
        file.write(config_yaml)

    #Copiar al contenedor
    subprocess.run(["lxc", "file", "push", "static/files/50-cloud-init.yaml", "lb/etc/netplan/50-cloud-init.yaml"], check=True)

    #Aplicar configuración dentro del contenedor ?????
    subprocess.run(["lxc", "exec", "lb", "--", "netplan", "apply"], check=True)

def change_netplan_hand(name):
    subprocess.run(["lxc", "exec", name , "--", "nano", "/etc/netplan/50-cloud-init.yaml"], check=True)


def change_netplan(name):
    # Desactivar cloud-init
    subprocess.run(f"lxc exec {name} -- bash -c 'echo \"network: {{config: disabled}}\" > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg'", shell=True, check=True)

    # Realizamos una copia de seguridad del archivo original
    subprocess.run(f"lxc exec {name} -- cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.bak", shell=True, check=True)

    if name == VM_NAMES["balanceador"]:
        # Configuración de la interfaz eth1
        netplan_config = """
        network:
            version: 2
            ethernets:
                eth0:
                    dhcp4: true
                eth1:
                    dhcp4: true
        """

    elif name == VM_NAMES["cliente"]:
        netplan_config = """
        network:
            version: 2
            ethernets:
                eth1:
                    dhcp4: true
        """

    # Escribimos la nueva configuración en el archivo
    subprocess.run(f"echo \"{netplan_config}\" | lxc exec {name} -- tee /etc/netplan/50-cloud-init.yaml", shell=True, check=True)

    # Reiniciamos el contenedor para asegurar que la configuración sea aplicada
    subprocess.run(f"lxc restart {name}", shell=True, check=True)
    print(f"Configuración de red aplicada en el contenedor {name}.")