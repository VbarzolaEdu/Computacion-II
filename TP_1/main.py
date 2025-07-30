from multiprocessing import Process, Pipe, Queue
from generador import generar_datos
from analizador import analizador
from verificador import verificador
from verificar_cadena import validar_integridad

if __name__ == "__main__":
    from time import sleep
    import os

    # Pipes hacia analizadores
    parent_a, child_a = Pipe()
    parent_b, child_b = Pipe()
    parent_c, child_c = Pipe()

    # Queues desde analizadores
    queue_a = Queue()
    queue_b = Queue()
    queue_c = Queue()

    # Lanzar procesos
    p_gen = Process(target=generar_datos, args=(parent_a, parent_b, parent_c))
    p_a = Process(target=analizador, args=("frecuencia", child_a, queue_a))
    p_b = Process(target=analizador, args=("presion", child_b, queue_b))
    p_c = Process(target=analizador, args=("oxigeno", child_c, queue_c))
    p_verif = Process(target=verificador, args=(queue_a, queue_b, queue_c))

    for p in [p_gen, p_a, p_b, p_c, p_verif]:
        p.start()

    for p in [p_gen, p_a, p_b, p_c, p_verif]:
        p.join()

    # Verificar la integridad de la blockchain después de completar los 60 bloques
    print("\n" + "="*50)
    print("VERIFICACIÓN DE INTEGRIDAD DE LA BLOCKCHAIN")
    print("="*50)
    
    resultado = validar_integridad("blockchain.json")
    
    if resultado:
        print("✅ La blockchain se ha creado correctamente y es válida")
    else:
        print("❌ Se detectaron problemas en la blockchain")
