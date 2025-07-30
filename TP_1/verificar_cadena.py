import json
from verificador import calcular_hash
import os

def validar_integridad(path="blockchain.json"):
    with open(path, "r") as f:
        cadena = json.load(f)

    for i in range(1, len(cadena)):
        bloque_actual = cadena[i]
        bloque_anterior = cadena[i-1]

        hash_recalculado = calcular_hash(
            bloque_anterior["hash"],
            bloque_actual["datos"],
            bloque_actual["timestamp"]
        )

        if bloque_actual["prev_hash"] != bloque_anterior["hash"]:
            print(f"Error en bloque #{i+1}: hash anterior no coincide")
            return False

        if bloque_actual["hash"] != hash_recalculado:
            print(f"Error en bloque #{i+1}: el hash no es válido")
            return False

    print("Blockchain válida")
    return True
