import os
import time

file_path = "comunicacion.txt"

def proceso_hijo():
    print("[Hijo] Esperando para leer el archivo...")
    time.sleep(1)  # Espera corta para simular condiciones de carrera
    try:
        with open(file_path, "r") as f:
            contenido = f.read()
            print(f"[Hijo] Leyó del archivo: {contenido}")
    except FileNotFoundError:
        print("[Hijo] El archivo no existe aún.")
    
    # Escribe algo en el archivo (sin sincronización)
    with open(file_path, "a") as f:
        f.write("\nMensaje del hijo.")

    print("[Hijo] Terminó.")

def proceso_padre():
    # Escribe algo en el archivo
    with open(file_path, "w") as f:
        f.write("Mensaje del padre.")

    print("[Padre] Escribió en el archivo.")
    time.sleep(2)  # Da tiempo al hijo a leer antes de continuar

    # Lee lo que hay en el archivo (posiblemente modificado por el hijo)
    with open(file_path, "r") as f:
        contenido = f.read()
        print(f"[Padre] Releyó del archivo: {contenido}")

    print("[Padre] Terminó.")

if __name__ == "__main__":
    pid = os.fork()

    if pid == 0:
        # Proceso hijo
        proceso_hijo()
    else:
        # Proceso padre
        proceso_padre()