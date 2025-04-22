import sys, subprocess
from consts import VALID_ORDERS, DEFAULT_SERVERS, MIN_SERVERS, MAX_SERVERS, IMAGE_DEFAULT
from ordenes import create_all, show_console, start_all, list_containers, delete_all, load_num_servers



"""
Configurar logs
"""






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

    ##

    # Determinar número de servidores
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
            n_servers = DEFAULT_SERVERS
    else:
        # Para órdenes distintas de create, cargamos el número guardado
        try:
            n_servers = load_num_servers()
        except FileNotFoundError:
            print("No se ha encontrado información de servidores. Ejecuta primero 'create'.")
            return

    #CREATE

    if orden == "create":
        create_all(n_servers=n_servers)
    elif orden == "start":
        start_all(n_servers=n_servers)
        show_console(n_servers)
    
    elif orden == "list":
        list_containers()

    elif orden == "delete":
        delete_all(n_servers=n_servers)


if __name__ == "__main__":
    main()