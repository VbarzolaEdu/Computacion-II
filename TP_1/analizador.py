from collections import deque
import numpy as np

def analizador(tipo, pipe_entrada, queue_salida):
    """
    tipo: 'frecuencia', 'presion' o 'oxigeno'
    pipe_entrada: conexión Pipe desde el generador
    queue_salida: Queue para enviar resultados al verificador
    """
    ventana = deque(maxlen=30)

    while True:
        try:
            muestra = pipe_entrada.recv()
            if muestra is None:
                break  
        except EOFError:
            break  
        except Exception as e:
            # Cualquier otro error
            print(f"Analizador {tipo}: Error inesperado: {e}")
            break  

        timestamp = muestra["timestamp"]

        if tipo == "frecuencia":
            valor = muestra["frecuencia"]
        elif tipo == "presion":
            sistolica, diastolica = muestra["presion"]
            valor = (sistolica + diastolica) / 2
        elif tipo == "oxigeno":
            valor = muestra["oxigeno"]
        else:
            continue  # tipo inválido

        # Agregar valor a la ventana móvil
        ventana.append(valor)

        # Calcular estadísticas solo si hay suficientes datos (puede ser >=1)
        if len(ventana) > 0:
            media = float(np.mean(ventana))
            desv = float(np.std(ventana))
        else:
            media, desv = 0.0, 0.0

        # Enviar resultado al verificador
        resultado = {
            "tipo": tipo,
            "timestamp": timestamp,
            "media": media,
            "desv": desv
        }

        queue_salida.put(resultado)
    

