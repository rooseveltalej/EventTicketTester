import socket
import threading
import time
import random

class AutomaticStadiumClient:
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

    def reservar_asientos_automaticamente(self, cantidad, zonas, categorias, categoria_actual=0):
        if categoria_actual >= len(categorias):
            print("No hay más categorías disponibles para revisar.")
            return

        for zona in zonas:
            for fila in range(1, 8):
                for asiento in range(1, 6):
                    command_check = f'CHECK_ASIENTO "{categorias[categoria_actual]}" "{zona}" {fila} {asiento}'
                    self.send_command(command_check)
                    time.sleep(0.5)

                    if self.asiento_disponible:
                        asiento_reserva = {
                            "categoria": categorias[categoria_actual], 
                            "zona": zona, 
                            "fila": str(fila), 
                            "asiento": str(asiento)
                        }
                        self.reservas.append(asiento_reserva)
                        command_reserve = f'RESERVAR_ASIENTO "{categorias[categoria_actual]}" "{zona}" {fila} {asiento}'
                        self.send_command(command_reserve)
                        time.sleep(1)

                        cantidad -= 1
                        if cantidad == 0:
                            self.send_command("GET_STADIUM_STRUCTURE")
                            return

        self.reservar_asientos_automaticamente(cantidad, zonas, categorias, categoria_actual + 1)

    def run_automatic(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.send_command("GET_STADIUM_STRUCTURE")

        while True:
            time.sleep(random.uniform(1, 5))  # Esperar entre 1 y 5 segundos entre comandos

            action = random.choice(["RESERVAR", "CHECK"])
            zonas = ["A", "B", "C", "D"]
            categorias = ["VIP", "Platea", "Sol", "Regular"]

            if action == "RESERVAR":
                cantidad = random.randint(1, 3)
                print(f"Reservar {cantidad} asientos...")
                self.reservar_asientos_automaticamente(cantidad, zonas, categorias)

                if self.reservas:
                    # Decidir aleatoriamente si comprar o no los asientos reservados
                    buy_decision = random.choice([True, False])
                    if buy_decision:
                        for asiento in self.reservas:
                            command = f'COMPRAR_ASIENTO "{asiento["categoria"]}" "{asiento["zona"]}" {asiento["fila"]} {asiento["asiento"]}'
                            self.send_command(command)
                        print("Compra realizada con éxito.")
                    else:
                        print("No se realizó la compra.")
                    
                    self.reservas.clear()
                    self.send_command("GET_STADIUM_STRUCTURE")
                    break  # Salir del programa después de la compra o decisión de no comprar

            elif action == "CHECK":
                zona = random.choice(zonas)
                categoria = random.choice(categorias)
                fila = random.randint(1, 7)
                asiento = random.randint(1, 5)
                command_check = f'CHECK_ASIENTO "{categoria}" "{zona}" {fila} {asiento}'
                self.send_command(command_check)

if __name__ == "__main__":
    client = AutomaticStadiumClient('127.0.0.1', 8080)  # Asegúrate de usar el puerto correcto
    client.run_automatic()
