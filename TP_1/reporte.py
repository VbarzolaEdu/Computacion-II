import json

def generar_reporte(path="blockchain.json", salida="reporte.txt"):
    with open(path, "r") as f:
        cadena = json.load(f)

    total_bloques = len(cadena)
    bloques_con_alerta = 0

    suma_frecuencia = 0
    suma_presion = 0
    suma_oxigeno = 0

    for bloque in cadena:
        datos = bloque["datos"]

        if bloque.get("alerta"):
            bloques_con_alerta += 1

        suma_frecuencia += datos["frecuencia"]["media"]
        suma_presion += datos["presion"]["media"]
        suma_oxigeno += datos["oxigeno"]["media"]

    promedio_frecuencia = suma_frecuencia / total_bloques
    promedio_presion = suma_presion / total_bloques
    promedio_oxigeno = suma_oxigeno / total_bloques

    with open(salida, "w") as f:
        f.write("📄 REPORTE FINAL DEL SISTEMA BIOMÉTRICO\n")
        f.write("="*40 + "\n")
        f.write(f"🔢 Total de bloques generados: {total_bloques}\n")
        f.write(f"⚠️  Bloques con alerta: {bloques_con_alerta}\n\n")
        f.write(f"📊 Promedios generales:\n")
        f.write(f"   - Frecuencia: {promedio_frecuencia:.2f}\n")
        f.write(f"   - Presión:    {promedio_presion:.2f}\n")
        f.write(f"   - Oxígeno:    {promedio_oxigeno:.2f}\n")
