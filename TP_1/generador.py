import time
import random
from datetime import datetime

def generar_datos(pipe_a, pipe_b, pipe_c):
    for i in range(60):
        muestra = {
            "timestamp": datetime.now().isoformat(),
            "frecuencia": random.randint(60, 180),
            "presion": (random.randint(100, 140), random.randint(60, 90)),
            "oxigeno": round(random.uniform(91.0, 99.9), 1)
        }

        pipe_a.send(muestra)
        pipe_b.send(muestra)
        pipe_c.send(muestra)

        time.sleep(1)
    
    # Cerrar los pipes para indicar que no habrá más datos
    pipe_a.close()
    pipe_b.close()
    pipe_c.close()
