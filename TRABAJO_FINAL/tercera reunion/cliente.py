"""
Cliente TCP interactivo para hacer reservas.
Permite elegir canchas, horarios y conectarse al servidor.

Uso:
    python cliente.py --host 127.0.0.1 --port 5000
    python cliente.py --host ::1 --port 5000           (IPv6)
    python cliente.py --host localhost --port 5000
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from data import CANCHAS, HORARIOS_DISPONIBLES, FECHAS_DISPONIBLES


class ClienteReservas:
    """Cliente interactivo para hacer reservas"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def conectar(self) -> bool:
        """Conecta al servidor TCP"""
        try:
            print(f"\n📡 Conectando a {self.host}:{self.port}...")
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            print(f"✅ Conectado exitosamente a {self.host}:{self.port}\n")
            return True
        except ConnectionRefusedError:
            print(f"❌ No se pudo conectar a {self.host}:{self.port}")
            print("   Asegúrate que el servidor está corriendo")
            return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def mostrar_menu_canchas(self) -> str:
        """Muestra menú de canchas y retorna cancha_id elegida"""
        print("\n🏟️  CANCHAS DISPONIBLES:")
        print("-" * 60)

        canchas_list = list(CANCHAS.items())
        for idx, (cancha_id, datos) in enumerate(canchas_list, 1):
            print(
                f"{idx}. {datos['nombre']:<30} "
                f"(${datos['precio_por_hora']}/h) - {datos['ubicacion']}"
            )

        while True:
            try:
                opcion = input(f"\nElige cancha (1-{len(canchas_list)}): ")
                opcion_num = int(opcion) - 1

                if 0 <= opcion_num < len(canchas_list):
                    cancha_id = canchas_list[opcion_num][0]
                    cancha = CANCHAS[cancha_id]
                    print(f"✅ Cancha seleccionada: {cancha['nombre']}")
                    return cancha_id
                else:
                    print(f"❌ Opción inválida. Ingresa entre 1 y {len(canchas_list)}")
            except ValueError:
                print("❌ Ingresa un número válido")

    def mostrar_menu_horarios(self) -> str:
        """Muestra menú de horarios y retorna horario elegido"""
        print("\n⏰ HORARIOS DISPONIBLES:")
        print("-" * 60)

        horarios_list = HORARIOS_DISPONIBLES
        for idx, horario in enumerate(horarios_list, 1):
            print(f"{idx:2}. {horario}", end="  ")
            if idx % 4 == 0:
                print()

        print()

        while True:
            try:
                opcion = input(f"\nElige horario (1-{len(horarios_list)}): ")
                opcion_num = int(opcion) - 1

                if 0 <= opcion_num < len(horarios_list):
                    horario = horarios_list[opcion_num]
                    print(f"✅ Horario seleccionado: {horario}")
                    return horario
                else:
                    print(f"❌ Opción inválida. Ingresa entre 1 y {len(horarios_list)}")
            except ValueError:
                print("❌ Ingresa un número válido")

    def mostrar_menu_fechas(self) -> str:
        """Muestra menú de fechas y retorna fecha elegida"""
        print("\n📅 FECHAS DISPONIBLES:")
        print("-" * 60)

        fechas_list = FECHAS_DISPONIBLES
        for idx, fecha in enumerate(fechas_list, 1):
            print(f"{idx}. {fecha}")

        while True:
            try:
                opcion = input(f"\nElige fecha (1-{len(fechas_list)}): ")
                opcion_num = int(opcion) - 1

                if 0 <= opcion_num < len(fechas_list):
                    fecha = fechas_list[opcion_num]
                    print(f"✅ Fecha seleccionada: {fecha}")
                    return fecha
                else:
                    print(f"❌ Opción inválida. Ingresa entre 1 y {len(fechas_list)}")
            except ValueError:
                print("❌ Ingresa un número válido")

    def obtener_cliente_id(self) -> str:
        """Solicita ID del cliente"""
        print("\n👤 CLIENTE:")
        print("-" * 60)

        cliente_id = input("Ingresa tu ID de cliente (ej: cliente_001): ").strip()

        if not cliente_id:
            print("❌ ID de cliente no puede estar vacío")
            return self.obtener_cliente_id()

        return cliente_id

    def obtener_precio(self, cancha_id: str) -> float:
        """Obtiene el precio de la cancha"""
        cancha = CANCHAS.get(cancha_id)
        return cancha["precio_por_hora"] if cancha else 0.0

    async def enviar_reserva(self, request: Dict[str, Any]) -> bool:
        """Envía la reserva al servidor y recibe respuesta"""
        try:
            # Convertir request a JSON
            json_data = json.dumps(request)
            print(f"\n📤 Enviando reserva...")
            print(f"   Datos: {json_data}")

            # Enviar al servidor
            self.writer.write(json_data.encode() + b"\n")
            await self.writer.drain()

            # Recibir respuesta
            data = await self.reader.readline()

            if not data:
                print("❌ Servidor cerró la conexión sin responder")
                return False

            response = json.loads(data.decode())

            # Mostrar respuesta
            if response.get("estado") == "confirmada":
                print("\n✅ RESERVA CONFIRMADA")
                print(f"   ID: {response.get('reserva_id')}")
                print(f"   Cancha: {response.get('cancha_id')}")
                print(f"   Horario: {response.get('horario')}")
                print(f"   Confirmada en: {response.get('confirmada_en')}")
                return True
            else:
                print(f"\n❌ ERROR: {response.get('message', 'Error desconocido')}")
                return False

        except json.JSONDecodeError as e:
            print(f"❌ Error al procesar respuesta del servidor: {e}")
            return False
        except Exception as e:
            print(f"❌ Error al enviar reserva: {e}")
            return False

    async def ejecutar(self):
        """Ejecuta el flujo completo del cliente"""
        # Conectar al servidor
        if not await self.conectar():
            return

        try:
            while True:
                print("\n" + "=" * 60)
                print("🎫 SISTEMA DE RESERVA DE CANCHAS")
                print("=" * 60)

                # Obtener datos del usuario
                cliente_id = self.obtener_cliente_id()
                cancha_id = self.mostrar_menu_canchas()
                horario = self.mostrar_menu_horarios()
                fecha = self.mostrar_menu_fechas()
                precio = self.obtener_precio(cancha_id)

                # Construir request
                request = {
                    "cliente_id": cliente_id,
                    "cancha_id": cancha_id,
                    "horario": horario,
                    "fecha": fecha,
                    "precio": precio,
                }

                # Mostrar resumen antes de enviar
                print("\n📋 RESUMEN DE RESERVA:")
                print("-" * 60)
                print(f"Cliente: {cliente_id}")
                print(f"Cancha: {CANCHAS[cancha_id]['nombre']}")
                print(f"Horario: {horario}")
                print(f"Fecha: {fecha}")
                print(f"Precio: ${precio}")

                confirmacion = input("\n¿Enviar esta reserva? (s/n): ").strip().lower()

                if confirmacion != "s":
                    print("❌ Reserva cancelada")
                    continue

                # Enviar reserva
                exito = await self.enviar_reserva(request)

                if exito:
                    otra = (
                        input(
                            "\n¿Deseas hacer otra reserva? (s/n): "
                        )
                        .strip()
                        .lower()
                    )
                    if otra != "s":
                        print(
                            "\n👋 ¡Gracias por usar el sistema! Hasta pronto."
                        )
                        break
                else:
                    reintentar = (
                        input("\n¿Reintentar? (s/n): ").strip().lower()
                    )
                    if reintentar != "s":
                        break

        except KeyboardInterrupt:
            print("\n\n👋 Cliente interrumpido por el usuario")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
        finally:
            self.desconectar()

    def desconectar(self):
        """Cierra la conexión con el servidor"""
        if self.writer:
            self.writer.close()
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(self.writer.wait_closed())
            except:
                pass
            print("✓ Desconectado del servidor")


async def main():
    """Entry point del cliente"""
    parser = argparse.ArgumentParser(
        description="Cliente TCP para sistema de reserva de canchas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python cliente.py --host 127.0.0.1 --port 5000    (IPv4)
  python cliente.py --host ::1 --port 5000           (IPv6 localhost)
  python cliente.py --host 0.0.0.0 --port 5000       (Cualquier IPv4)
  python cliente.py --host :: --port 5000            (Cualquier IPv6)
        """,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host del servidor (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto del servidor (default: 5000)",
    )

    args = parser.parse_args()

    print(f"\n🚀 Iniciando cliente...")
    print(f"   Host: {args.host}")
    print(f"   Puerto: {args.port}\n")

    cliente = ClienteReservas(args.host, args.port)
    await cliente.ejecutar()


if __name__ == "__main__":
    asyncio.run(main())
