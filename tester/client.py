import socket
import threading
import time

# Lista para almacenar los asientos reservados temporalmente
reservas = []

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

def reservar_asientos_automaticamente(sock, cantidad):
    global reservas
    for i in range(cantidad):
        zona = "A"  # Puedes cambiar esto según tus necesidades
        categoria = "VIP"  # Puedes cambiar esto según tus necesidades
        fila = str(i + 1)  # Asignar filas secuencialmente
        asiento = str(i + 1)  # Asignar asientos secuencialmente
        asiento_reserva = {"categoria": categoria, "zona": zona, "fila": fila, "asiento": asiento}
        reservas.append(asiento_reserva)

        # Enviar comando de reserva al servidor
        command = f'RESERVAR_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
        send_command(sock, command)
        time.sleep(1)  # Esperar un segundo entre reservas para evitar sobrecargar el servidor

    # Solicitar la estructura del estadio después de reservar
    send_command(sock, "GET_STADIUM_STRUCTURE")

def main():
    global reservas
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8080))

    # Enviar la solicitud de estructura del estadio inmediatamente
    send_command(client_socket, "GET_STADIUM_STRUCTURE")

    # Iniciar el hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        print("\nOpciones:")
        print("1. Reservar Asiento")
        print("2. Comprar Asiento(s) Reservado(s)")
        print("3. Reservar Asientos Automáticamente")
        print("4. Salir")
        choice = input("Seleccione una opción: ")

        if choice == '1':
            try:
                cantidad = int(input("Ingrese la cantidad de asientos a reservar (máximo 3): "))
                if cantidad < 1 or cantidad > 3:
                    print("Error: Solo se pueden reservar entre 1 y 3 asientos.")
                    continue

                for i in range(cantidad):
                    zona = input(f"Ingrese la zona para el asiento {i+1}: ")
                    categoria = input(f"Ingrese la categoría para el asiento {i+1}: ")
                    fila = input(f"Ingrese la fila para el asiento {i+1}: ")
                    asiento = input(f"Ingrese el número de asiento para el asiento {i+1}: ")
                    asiento_reserva = {"categoria": categoria, "zona": zona, "fila": fila, "asiento": asiento}
                    reservas.append(asiento_reserva)

                    # Enviar comando de reserva al servidor
                    command = f'RESERVAR_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
                    send_command(client_socket, command)

                # Solicitar la estructura del estadio después de reservar
                send_command(client_socket, "GET_STADIUM_STRUCTURE")
            
            except ValueError:
                print("Error: La cantidad de asientos debe ser un número entero.")

        elif choice == '2':
            if reservas:
                for asiento in reservas:
                    command = f'COMPRAR_ASIENTO "{asiento["categoria"]}" "{asiento["zona"]}" {asiento["fila"]} {asiento["asiento"]}'
                    send_command(client_socket, command)
                
                # Limpiar la lista de reservas después de la compra
                reservas.clear()

                # Solicitar la estructura del estadio después de la compra
                send_command(client_socket, "GET_STADIUM_STRUCTURE")
                print("Compra realizada con éxito.")
            else:
                print("No hay asientos reservados para comprar.")

        elif choice == '3':
            try:
                cantidad = int(input("Ingrese la cantidad de asientos a reservar automáticamente (máximo 3): "))
                if cantidad < 1 or cantidad > 3:
                    print("Error: Solo se pueden reservar entre 1 y 3 asientos.")
                    continue

                reservar_asientos_automaticamente(client_socket, cantidad)
            
            except ValueError:
                print("Error: La cantidad de asientos debe ser un número entero.")

        elif choice == '4':
            print("Saliendo...")
            client_socket.close()
            break

        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()
