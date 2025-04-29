import os
import signal
import time

# Variable global para indicar que se recibió la señal
señal_recibida = False

def manejador_senal(signum, frame):
    global señal_recibida
    print(f"[Padre] Señal {signum} recibida. Continuando ejecución...")
    señal_recibida = True

def proceso_principal():
    # Registrar el manejador para SIGUSR1
    signal.signal(signal.SIGUSR1, manejador_senal)

    pid = os.fork()  # Crear proceso hijo

    if pid == 0:
        # Código del hijo
        print(f"[Hijo] PID {os.getpid()} iniciado.")
        print("[Hijo] Simulando tarea...")
        time.sleep(2)
        print(f"[Hijo] Enviando señal al padre (PID {os.getppid()})...")
        os.kill(os.getppid(), signal.SIGUSR1)
        print("[Hijo] Terminando.")
        os._exit(0)
    else:
        # Código del padre
        print(f"[Padre] Esperando señal de hijo (PID {pid})...")
        while not señal_recibida:
            time.sleep(0.1)  # Espera activa breve
        print("[Padre] Ejecutando después de la señal.")
        os.wait()  # Esperar la terminación del hijo

if __name__ == "__main__":
    proceso_principal()
