import signal
import time

# Paso 1: Definir un manejador de señal
def manejador_SIGINT(signum, frame):
    print(f"\n¡Señal recibida! Número: {signum}")
    print("Terminando el programa de manera controlada.")
    exit(0)

# Paso 2: Asociar la señal SIGINT al manejador
signal.signal(signal.SIGINT, manejador_SIGINT)

# Paso 3: Loop de ejecución
print("Presioná Ctrl+C para enviar SIGINT.")
while True:
    time.sleep(1)
    print("Trabajando...")
