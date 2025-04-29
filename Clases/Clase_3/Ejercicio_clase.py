#EJERCICIO CLASES

import os
import time

pid1 = os.fork()  # Crear el primer hijo

if pid1 == 0:  # Código del primer hijo
    time.sleep(2)
    print(f"Soy el uno, mi PID es {os.getpid()}")
    os._exit(0)  # Terminar el proceso hijo

pid2 = os.fork()  # Crear el segundo hijo

if pid2 == 0:  # Código del segundo hijo
    time.sleep(3)
    print(f"Soy el dos, mi PID es {os.getpid()}")
    os._exit(0)  # Terminar el proceso hijo

# Código del padre (no espera a los hijos)
print(f"Soy el padre, termino, mi PID es {os.getpid()}")

"""
import os
import time

def create_child(wait_time, message):
    pid = os.fork()
    if pid == 0:  # Código del hijo
        time.sleep(wait_time)
        print(f"{message}, mi PID es {os.getpid()}, el PID de mi padre es {os.getppid()}")
        os._exit(0)

if __name__ == "__main__":
    create_child(2, "Soy el hijo 1")
    create_child(3, "Soy el hijo 2")

    # time.sleep(2)
    print(f"Soy el padre, mi PID es {os.getpid()}")
"""
