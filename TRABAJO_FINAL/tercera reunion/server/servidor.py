"""
Servidor asyncio principal.
Escucha conexiones TCP, recibe JSON de clientes, maneja el event loop.
"""
import asyncio
import json
import logging
from typing import Optional

from utils.config import Config
from utils.logger import get_logger
from server.handlers import handle_client
from server.dispatcher import Dispatcher
from workers.workers import WorkerPool
import socket


logger = get_logger(__name__)


class AsyncioServer:
    """Servidor TCP con asyncio y ProcessPoolExecutor para workers"""

    def __init__(self, config: Config):
        self.config = config  # Configuración centralizada
        self.worker_pool: Optional[WorkerPool] = None
        self.dispatcher: Optional[Dispatcher] = None
        self.server = None



    def get_socket_family(self,host:str) -> int:
        """
        Detectar si el host es IPv4 o IPv6.
        Retorna socket.AF_INET para IPv4 o socket.AF_INET6 para IPv6.
        """
        try:
            # Intentar parsear como IPv6
            socket.inet_pton(socket.AF_INET6, host)
            return socket.AF_INET6
        except (socket.error, OSError):
            pass

        try:
            # Intentar parsear como IPv4
            socket.inet_pton(socket.AF_INET, host)
            return socket.AF_INET
        except (socket.error, OSError):
            pass

        # Si es "::" (escuchar en todos), usar IPv6 con dual-stack
        if host == "::":
            return socket.AF_INET6

        # Default: IPv4
        return socket.AF_INET


    def _configure_dual_stack(self):
        """
        Configurar socket para soportar IPv4 e IPv6 simultáneamente.
        Retorna una función que configura el socket.
        """
        def set_socket_opts(sock):
            # Permitir reutilizar dirección/puerto
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Si es IPv6, habilitar dual-stack (aceptar IPv4 también)
            if sock.family == socket.AF_INET6:
                # IPV6_V6ONLY=0 permite que IPv6 acepte conexiones IPv4
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                logger.info("✓ Dual-stack habilitado (IPv4 + IPv6)")

        return set_socket_opts

    async def start(self):
        """Inicia el servidor TCP y el dispatcher"""
        logger.info(f"Iniciando servidor en {self.config.HOST}:{self.config.PORT}")

        # Crear y configurar el pool de workers
        self.worker_pool = WorkerPool(self.config.NUM_WORKERS)
        self.worker_pool.create()

        # Crear dispatcher con el executor del pool
        self.dispatcher = Dispatcher(self.worker_pool.executor)

        # Crear socket manualmente para habilitar dual-stack (IPv4 + IPv6)
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Habilitar dual-stack: IPv6 socket que también acepta IPv4
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.bind(("::", self.config.PORT))
        sock.listen(128)

        # Iniciar servidor TCP con el socket configurado
        self.server = await asyncio.start_server(
            self._client_connected,
            sock=sock
        )

        # Loguear información de los sockets
        sock_info = self.server.sockets[0]
        addr = sock_info.getsockname()
        logger.info(f"Servidor escuchando en {addr}")
        logger.info(f"✓ Dual-stack habilitado (acepta IPv4 e IPv6)")

        async with self.server:
            await self.server.serve_forever()

    async def _client_connected(self, reader, writer):
        """Callback cuando se conecta un cliente"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Cliente conectado: {addr}")

        try:
            # Le paso al dispatcher para que lo maneje
            # El dispatcher se encarga de asignar a un worker
            await handle_client(reader, writer, self.dispatcher)
        except Exception as e:
            logger.error(f"Error manejando cliente {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Cliente desconectado: {addr}")


    async def stop(self):
        """Detiene el servidor y libera recursos"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self.worker_pool:
            self.worker_pool.shutdown(wait=True)

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
