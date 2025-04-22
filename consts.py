"""
CONSTS
"""

VALID_ORDERS=['create', 'start', 'list', 'delete']
NUM_SERVERS_FILE="static/files/num_serves.txt"
DEFAULT_SERVERS=2
MIN_SERVERS=1
MAX_SERVERS=5

IMAGE_DEFAULT = "ubuntu2004"

VM_NAMES = {
    "cliente": "cl",
    "balanceador": "lb",
    "servidores": ["s1", "s2", "s3", "s4", "s5"]
}

BRIDGES = {
    "LAN1": "lxdbr0",
    "LAN2": "lxdbr1"
}

BRIDGES_IPV4 = {
    "lxdbr0": "134.3.0.1/24",
    "lxdbr1": "134.3.1.1/24"
}

IP_LB = {
    "eth0": "134.3.0.10",
    "eth1": "134.3.1.10"
}