import sys, subprocess
from consts import VALID_ORDERS, DEFAULT_SERVERS, MIN_SERVERS, MAX_SERVERS, IMAGE_DEFAULT
from ordenes import create_all, start_all, list_containers, delete_all, stop_all, create_server, delete_last_server, start_server, stop_server
from utils.file import load_num_servers
from utils.console import show_consoles, show_console, close_consoles

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 pfinal1.py <orden> [número de servidores]")
        return

    orden = sys.argv[1]
    if orden not in VALID_ORDERS:
        print(f"Orden no válida. Usa alguna de: {VALID_ORDERS}")
        return
    
    
    """
    Iniciar sesiones e imágenes
    """


    #Determinar número de servidores
    if orden == "create":
        if len(sys.argv) == 3:
            try:
                n_servers = int(sys.argv[2])
                if not (MIN_SERVERS <= n_servers <= MAX_SERVERS):
                    raise ValueError()
            except ValueError:
                print(f"El número de servidores debe estar entre {MIN_SERVERS} y {MAX_SERVERS}.")
                return
        else:
            #Para cuando no haya un número de servidores, se pone el default 
            n_servers = DEFAULT_SERVERS
    else:
        #Para órdenes distintas de create, cargamos el número guardado
        try:
            n_servers = load_num_servers()
        except FileNotFoundError:
            print("No se ha encontrado información de servidores. Ejecuta primero 'create'.")
            return

   #ORDENES 

    if orden == "create":
        create_all(n_servers=n_servers)

    elif orden == "start":
        start_all(n_servers=n_servers)
        show_consoles(n_servers=n_servers)
    
    elif orden == "list":
        list_containers()

    elif orden == "delete":
        delete_all(n_servers=n_servers)

    elif orden == "stop":
        stop_all(n_servers=n_servers)
        close_consoles(n_servers=n_servers)

    elif orden == "create_server":
        create_server()
        n_servers = n_servers + 1 
    
    elif orden == "delete_last_server":
        delete_last_server()
        n_servers = n_servers - 1

    elif orden == "start_server":
        if len(sys.argv) < 3:
            print("Uso: python3 pfinal1.py start_server <nombre_servidor>")
            sys.exit(1)
        name = sys.argv[2]
        start_server(name=name)
        show_console(name=name)
    
    elif orden == "stop_server":
        if len(sys.argv) < 3:
            print("Uso: python3 pfinal1.py stop_server <nombre_servidor>")
            sys.exit(1)
        name = sys.argv[2]
        stop_server(name=name)

if __name__ == "__main__":
    main()