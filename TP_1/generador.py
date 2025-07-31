import time
import random
from datetime import datetime

def generar_datos(pipe_a, pipe_b, pipe_c):
    for i in range(60):
        muestra = {
            "timestamp": datetime.now().isoformat(),
            "frecuencia": random.randint(60, 180),
            "presion": (random.randint(100, 140), random.randint(60, 90)),
            "oxigeno": round(random.uniform(90.0, 100.0), 1)
        }

        pipe_a.send(muestra)
        pipe_b.send(muestra)
        pipe_c.send(muestra)

        time.sleep(1)
    
    
    pipe_a.send(None)  # Señal de terminación para el analizador de frecuencia
    pipe_b.send(None)  # Señal de terminación para el analizador de presión
    pipe_c.send(None)  # Señal de terminación para el analizador de oxígeno

    #se cierra el pipe pero se manda señal de none para manejar excepcion del analizador correctamente
    pipe_a.close()
    pipe_b.close()
    pipe_c.close()
