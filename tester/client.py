import socket
import threading
import time

class StadiumClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.reservas = []
        self.asiento_disponible = False

    def send_command(self, command):
        try:
            self.client_socket.sendall(f"{command}\n".encode('utf-8'))
        except Exception as e:
            print(f"Error sending command: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(4096).decode('utf-8')
                if message:
                    print(message)
                    if "ASIENTO_DISPONIBLE" in message:
                        self.asiento_disponible = "true" in message.lower()
                else:
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def reservar_asientos_automaticamente(self, cantidad):
        categorias = ["VIP", "Regular", "Sol", "Platea"]
        reservado = False

        for i in range(cantidad):
            for categoria in categorias:
                if reservado:
                    break
                for fila in range(1, 4):  # Suponiendo un máximo de 7 filas
                    if reservado:
                        break
                    for asiento in range(1, 6):  # Suponiendo un máximo de 5 asientos por fila
                        # Verificar disponibilidad del asiento antes de reservar
                        command_check = f'CHECK_ASIENTO "{categoria}" "A" {fila} {asiento}'
                        self.send_command(command_check)
                        time.sleep(0.5)  # Esperar respuesta del servidor

                        if self.asiento_disponible:
                            asiento_reserva = {"categoria": categoria, "zona": "A", "fila": str(fila), "asiento": str(asiento)}
                            self.reservas.append(asiento_reserva)
                            command_reserve = f'RESERVAR_ASIENTO "{categoria}" "A" {fila} {asiento}'
                            self.send_command(command_reserve)
                            time.sleep(1)  # Esperar un segundo entre reservas para evitar sobrecargar el servidor
                            reservado = True
                            break

            if not reservado:
                print("No hay asientos disponibles en ninguna categoría.")
                return
            else:
                reservado = False  # Resetear para la siguiente iteración

        # Solicitar la estructura del estadio después de reservar
        self.send_command("GET_STADIUM_STRUCTURE")

    def run(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.send_command("GET_STADIUM_STRUCTURE")

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
                        self.reservas.append(asiento_reserva)

                        command = f'RESERVAR_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
                        self.send_command(command)

                    self.send_command("GET_STADIUM_STRUCTURE")
                
                except ValueError:
                    print("Error: La cantidad de asientos debe ser un número entero.")

            elif choice == '2':
                if self.reservas:
                    for asiento in self.reservas:
                        command = f'COMPRAR_ASIENTO "{asiento["categoria"]}" "{asiento["zona"]}" {asiento["fila"]} {asiento["asiento"]}'
                        self.send_command(command)
                    
                    self.reservas.clear()
                    self.send_command("GET_STADIUM_STRUCTURE")
                    print("Compra realizada con éxito.")
                else:
                    print("No hay asientos reservados para comprar.")

            elif choice == '3':
                try:
                    cantidad = int(input("Ingrese la cantidad de asientos a reservar automáticamente (máximo 3): "))
                    if cantidad < 1 or cantidad > 3:
                        print("Error: Solo se pueden reservar entre 1 y 3 asientos.")
                        continue

                    self.reservar_asientos_automaticamente(cantidad)
                
                except ValueError:
                    print("Error: La cantidad de asientos debe ser un número entero.")

            elif choice == '4':
                print("Saliendo...")
                self.client_socket.close()
                break

            else:
                print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    client = StadiumClient('127.0.0.1', 8080)
    client.run()
