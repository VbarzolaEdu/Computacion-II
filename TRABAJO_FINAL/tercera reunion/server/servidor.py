"""
Servidor asyncio principal.
Escucha conexiones TCP, recibe JSON de clientes, maneja el event loop.
"""
import asyncio
import json
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

from utils.config import Config
from utils.logger import get_logger
from server.handlers import handle_client
from server.dispatcher import Dispatcher

logger = get_logger(__name__)


class AsyncioServer:
    """Servidor TCP con asyncio y ProcessPoolExecutor para workers"""

    def __init__(self, config: Config):
        self.config = config //todavia no hay config
        self.executor: Optional[ProcessPoolExecutor] = None
        self.dispatcher: Optional[Dispatcher] = None
        self.server = None

    async def start(self):
        """Inicia el servidor TCP y el dispatcher"""
        logger.info(f"Iniciando servidor en {self.config.HOST}:{self.config.PORT}")

        # Crear executor con N workers
        self.executor = ProcessPoolExecutor(
            max_workers=self.config.NUM_WORKERS,
            initializer=self._init_worker
        )

        # Crear dispatcher
        self.dispatcher = Dispatcher(self.executor)

        # Iniciar servidor TCP
        self.server = await asyncio.start_server(
            self._client_connected,
            self.config.HOST,
            self.config.PORT
        )

        addr = self.server.sockets[0].getsockname()
        logger.info(f"Servidor escuchando en {addr}")

        async with self.server:
            await self.server.serve_forever()

    async def _client_connected(self, reader, writer):
        """Callback cuando se conecta un cliente"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Cliente conectado: {addr}")

        try:
            await handle_client(reader, writer, self.dispatcher) //Le paso al distpacher para que lo maneje, y el dispatcher se encarga de asignar a un worker
        except Exception as e:
            logger.error(f"Error manejando cliente {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Cliente desconectado: {addr}")


///Aca se inicializa cada worker pero habria que ver donde coloco la logica que permite la inicializacion de la db.
    def _init_worker(self):
        """Inicializador para cada worker (se ejecuta una sola vez)"""
        # Aquí puedes inicializar DB connections, loggers, etc. en cada proceso
        logger.info("Worker inicializado")

    async def stop(self):
        """Detiene el servidor y libera recursos"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self.executor:
            self.executor.shutdown(wait=True)

        logger.info("Servidor detenido")


async def main():
    """Entry point del servidor"""
    config = Config()
    server = AsyncioServer(config)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Interrupción del usuario")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
