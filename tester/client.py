import socket
import threading

def send_command(sock, command):
    try:
        sock.sendall(f"{command}\n".encode('utf-8'))
    except Exception as e:
        print(f"Error sending command: {e}")

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(4096).decode('utf-8')
            if message:
                print(message)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8080))

    # Enviar la solicitud de estructura del estadio inmediatamente
    send_command(client_socket, "GET_STADIUM_STRUCTURE")

    # Iniciar el hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        print("\nOpciones:")
        print("1. Reservar Asiento")
        print("2. Comprar Asiento")
        print("3. Salir")
        choice = input("Seleccione una opción: ")

        if choice == '1':
            categoria = input("Ingrese la categoría: ")
            zona = input("Ingrese la zona: ")
            fila = input("Ingrese la fila: ")
            asiento = input("Ingrese el número de asiento: ")
            command = f'RESERVAR_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
            send_command(client_socket, command)

        elif choice == '2':
            categoria = input("Ingrese la categoría: ")
            zona = input("Ingrese la zona: ")
            fila = input("Ingrese la fila: ")
            asiento = input("Ingrese el número de asiento: ")
            command = f'COMPRAR_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
            send_command(client_socket, command)

        elif choice == '3':
            print("Saliendo...")
            client_socket.close()
            break

        else:
            print("Opción no válida. Intente nuevamente.")

if _name_ == "_main_":
    main()