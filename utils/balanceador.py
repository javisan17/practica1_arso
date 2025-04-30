import subprocess
from logger import setup_logger, get_logger


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

def change_netplan(name):
    subprocess.run(["lxc", "exec", name , "--", "nano", "/etc/netplan/50-cloud-init.yaml"], check=True)

