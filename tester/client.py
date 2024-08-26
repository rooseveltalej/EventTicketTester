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

    def reservar_asientos_automaticamente(self, cantidad, zonas, categorias, zona_actual=0, categoria_actual=0):
        if zona_actual >= len(zonas):
            print("No hay más zonas disponibles para revisar.")
            return

        if categoria_actual >= len(categorias):
            # Pasar a la siguiente zona si se han revisado todas las categorías en la zona actual
            self.reservar_asientos_automaticamente(cantidad, zonas, categorias, zona_actual + 1, 0)
            return

        for fila in range(1, 4):  # Suponiendo un máximo de 3 filas
            for asiento in range(1, 6):  # Suponiendo un máximo de 5 asientos por fila
                # Verificar disponibilidad del asiento antes de reservar
                command_check = f'CHECK_ASIENTO "{categorias[categoria_actual]}" "{zonas[zona_actual]}" {fila} {asiento}'
                self.send_command(command_check)
                time.sleep(0.5)  # Esperar respuesta del servidor

                if self.asiento_disponible:
                    asiento_reserva = {
                        "categoria": categorias[categoria_actual], 
                        "zona": zonas[zona_actual], 
                        "fila": str(fila), 
                        "asiento": str(asiento)
                    }
                    self.reservas.append(asiento_reserva)
                    command_reserve = f'RESERVAR_ASIENTO "{categorias[categoria_actual]}" "{zonas[zona_actual]}" {fila} {asiento}'
                    self.send_command(command_reserve)
                    time.sleep(1)  # Esperar un segundo entre reservas para evitar sobrecargar el servidor

                    cantidad -= 1
                    if cantidad == 0:
                        # Si ya se han reservado todos los asientos requeridos, terminar la función
                        self.send_command("GET_STADIUM_STRUCTURE")
                        return

        # Si no se encontró asiento en la categoría actual, pasar a la siguiente categoría
        self.reservar_asientos_automaticamente(cantidad, zonas, categorias, zona_actual, categoria_actual + 1)


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

                    zonas = ["A", "B", "C", "D"]
                    categorias = ["VIP", "Regular", "Sol", "Platea"]
                    self.reservar_asientos_automaticamente(cantidad, zonas, categorias)
                
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
