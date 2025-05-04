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


# def change_netplan_hand(name):
#     """
#     Cambiar el archivo 50-cloud-init.yaml a mano desde un nano del contenedor name (qué será o el balanceador o el cliente)
#     """

#     subprocess.run(["lxc", "exec", name , "--", "nano", "/etc/netplan/50-cloud-init.yaml"], check=True)


def change_netplan(name):
    """
    Cambiar el archivo 50-cloud-init.yaml automáticamente del contenedor name (qué será o el balanceador o el cliente)
    """

    if name not in [VM_NAMES["balanceador"], VM_NAMES["cliente"]]:
        return

    #Desactivar el cloud-init presente en archivo 99-disable-network-config.cfg. Impide que el cloud-init reescriba la configuración de red
    subprocess.run(f"lxc exec {name} -- bash -c 'echo \"network: {{config: disabled}}\" > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg'", shell=True, check=True)

    #Realizar una copia de seguridad del archivo original
    subprocess.run(f"lxc exec {name} -- cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.bak", shell=True, check=True)

    if name == VM_NAMES["balanceador"]:
        #Configuración de la interfaz eth1 del balanceador
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
        #Configuración de la interfaz eth1 del cliente
        netplan_config = """
        network:
            version: 2
            ethernets:
                eth1:
                    dhcp4: true
        """

    #Escribir la nueva configuración en el archivo
    subprocess.run(f"echo \"{netplan_config}\" | lxc exec {name} -- tee /etc/netplan/50-cloud-init.yaml", shell=True, check=True)

    #Reiniciar el contenedor para asegurar que la configuración sea aplicada
    subprocess.run(f"lxc restart {name}", shell=True, check=True)
    logger.info(f"Configuración de red aplicada en el contenedor {name}.")