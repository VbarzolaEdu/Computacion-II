import json
import hashlib
import os
import queue

def calcular_hash(prev_hash, datos, timestamp):
    bloque_str = prev_hash + json.dumps(datos, sort_keys=True) + timestamp
    return hashlib.sha256(bloque_str.encode()).hexdigest()

def verificador(queue_a, queue_b, queue_c):
    from collections import defaultdict
    

    resultados_por_timestamp = defaultdict(dict)
    cadena_bloques = []

    # Leer blockchain existente si hay
    if os.path.exists("blockchain.json"):
        with open("blockchain.json", "r") as f:
            cadena_bloques = json.load(f)
    


    while True:
        if len(cadena_bloques) >= 60:
            break  # Terminó la prueba

        
        for q in [queue_a, queue_b, queue_c]:
            try:
                resultado = q.get(timeout=0.1)  # Timeout de 0.1 segundos
                timestamp = resultado["timestamp"]
                tipo = resultado["tipo"]
                media = resultado["media"]

                resultados_por_timestamp[timestamp][tipo] = resultado
            except queue.Empty:
                continue  # No hay datos en esta queue, continúa con la siguiente

        # Procesar timestamps completos (con los 3 resultados)
        timestamps_completos = [
            ts for ts, res in resultados_por_timestamp.items()
            if {"frecuencia", "presion", "oxigeno"} <= res.keys()
        ]

        for ts in sorted(timestamps_completos):
            datos = {
                "frecuencia": resultados_por_timestamp[ts]["frecuencia"],
                "presion": resultados_por_timestamp[ts]["presion"],
                "oxigeno": resultados_por_timestamp[ts]["oxigeno"]
            }

            # Validar rango
            alerta = False
            if datos["frecuencia"]["media"] >= 200:
                alerta = True
            if datos["presion"]["media"] >= 200:
                alerta = True
            if not (90 < datos["oxigeno"]["media"] <= 100):
                alerta = True

            prev_hash = cadena_bloques[-1]["hash"] if cadena_bloques else "0"*64
            nuevo_hash = calcular_hash(prev_hash, datos, ts)

            bloque = {
                "timestamp": ts,
                "datos": datos,
                "alerta": alerta,
                "prev_hash": prev_hash,
                "hash": nuevo_hash
            }

            cadena_bloques.append(bloque)
            print(f"Bloque #{len(cadena_bloques)} | Hash: {nuevo_hash[:8]}... | Alerta: {'Sí' if alerta else 'No'}")

            # Eliminar ese timestamp del buffer
            del resultados_por_timestamp[ts]

            # Guardar en archivo
            with open("blockchain.json", "w") as f:
                json.dump(cadena_bloques, f, indent=4)
