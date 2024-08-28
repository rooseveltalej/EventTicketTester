# Descripción General del Código

Este código implementa un cliente automático para un servidor de reservas de asientos en un estadio. Utiliza la biblioteca `socket` para la comunicación TCP y `threading` para manejar la recepción de mensajes de manera concurrente.

## Estructuras y Funciones Principales

### Clase `AutomaticStadiumClient`

- **`__init__`**: Inicializa el cliente, establece la conexión con el servidor y define algunas variables de estado.
- **`send_command`**: Envía comandos al servidor.
- **`receive_messages`**: Hilo que recibe mensajes del servidor de manera continua.
- **`reservar_asientos_automaticamente`**: Algoritmo que intenta reservar asientos automáticamente en diferentes zonas y categorías.
- **`run_automatic`**: Inicia el hilo de recepción de mensajes y ejecuta acciones automáticas de reserva y verificación de asientos.

## Algoritmo de Reserva de Asientos

El algoritmo de reserva de asientos se encuentra en la función `reservar_asientos_automaticamente`. Aquí está el desglose:

1. **Parámetros de Entrada**: `cantidad` (número de asientos a reservar), `zonas` (lista de zonas), `categorias` (lista de categorías), `categoria_actual` (índice de la categoría actual).
2. **Búsqueda de Asientos**:
   - Itera sobre las zonas y filas/asientos dentro de cada zona.
   - Envía un comando `CHECK_ASIENTO` para verificar la disponibilidad del asiento.
   - Si el asiento está disponible, lo reserva enviando un comando `RESERVAR_ASIENTO`.
   - Reduce la cantidad de asientos a reservar y, si llega a cero, solicita la estructura del estadio y termina.
3. **Recursión**: Si no se encuentran suficientes asientos en la categoría actual, la función se llama a sí misma con la siguiente categoría.

## Ejemplo de Uso

El método `run_automatic` inicia el proceso automático:

1. **Recepción de Mensajes**: Inicia un hilo para recibir mensajes del servidor.
2. **Acciones Automáticas**:
   - Espera un tiempo aleatorio entre 1 y 5 segundos.
   - Selecciona aleatoriamente entre las acciones "RESERVAR" y "CHECK".
   - Si selecciona "RESERVAR", intenta reservar entre 1 y 3 asientos.
   - Decide aleatoriamente si comprar los asientos reservados o liberarlos.

## Código de Ejemplo

```python
if __name__ == "__main__":
    client = AutomaticStadiumClient('127.0.0.1', 8080)  # Asegúrate de usar el puerto correcto
    client.run_automatic()
```