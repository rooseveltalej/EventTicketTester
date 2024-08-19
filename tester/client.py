import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(4096).decode('utf-8')  # Aumenta el buffer si es necesario
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
    client_socket.send("GET_STADIUM_STRUCTURE\n".encode('utf-8'))

    # Iniciar el hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Esperar para recibir mensajes (no hacer nada en el hilo principal)
    while True:
        pass  # Puedes reemplazar esto con cualquier lógica adicional si es necesario

if __name__ == "__main__":
    main()



