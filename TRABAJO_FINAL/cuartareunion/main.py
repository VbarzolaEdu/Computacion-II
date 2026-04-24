"""
Punto de entrada del servidor de reservas de pádel.

Orden de inicio:
  1. Parsear argumentos CLI
  2. Inicializar la base de datos (crea tablas y seed si no existen)
  3. Crear WorkerPool (ProcessPoolExecutor) — cada worker abre su conexión SQLite
  4. Crear AsyncioServer
  5. asyncio.run() → lanza el event loop
"""

import argparse
import asyncio

from database.init_db import init_db
from workers.pool import WorkerPool
from server.servidor import AsyncioServer

DB_PATH = "padel.db"


def parse_args():
    parser = argparse.ArgumentParser(description="Servidor de reservas de pádel")
    parser.add_argument("--port", type=int, default=8888, help="Puerto TCP (default: 8888)")
    parser.add_argument("--workers", type=int, default=3, help="Número de workers (default: 3)")
    return parser.parse_args()


async def run_servidor(servidor: AsyncioServer):
    try:
        await servidor.start()
    except KeyboardInterrupt:
        pass
    finally:
        await servidor.stop()
        print("[main] Listo. Hasta luego.")


if __name__ == "__main__":
    args = parse_args()

    print("=" * 50)
    print("  Servidor de Reservas de Pádel")
    print("=" * 50)
    print(f"  Puerto:  {args.port}")
    print(f"  Workers: {args.workers}")
    print(f"  Red:     dual-stack IPv4 + IPv6")
    print("=" * 50)

    # Inicializar DB antes que todo — crea tablas y seed de canchas/horarios
    init_db(DB_PATH)

    # El pool se crea ANTES de asyncio.run() — evita conflictos de fork en Linux.
    # Cada worker recibe db_path y abre su propia conexión SQLite en _init_worker().
    pool = WorkerPool(num_workers=args.workers, db_path=DB_PATH)
    pool.create()

    servidor = AsyncioServer(
        port=args.port,
        worker_pool=pool,
        db_path=DB_PATH,
    )

    try:
        asyncio.run(run_servidor(servidor))
    except KeyboardInterrupt:
        print("\n[main] Interrupción recibida, cerrando...")
    finally:
        pool.shutdown()
