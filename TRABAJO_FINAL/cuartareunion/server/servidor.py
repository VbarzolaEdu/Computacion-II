import asyncio
import socket

from server.handlers import handle_client
from server.dispatcher import Dispatcher


class AsyncioServer:
    """
    Servidor TCP con asyncio.

    Escucha conexiones entrantes y para cada cliente crea una corutina
    handle_client() que corre concurrentemente en el event loop.
    """

    def __init__(self, port: int, worker_pool, db_path: str):
        self.port = port
        self.worker_pool = worker_pool
        self.db_path = db_path
        self._server = None

    def _crear_socket(self) -> socket.socket:
        """
        Siempre intenta dual-stack (IPv4 + IPv6 en el mismo socket).

        Con IPV6_V6ONLY=0 el servidor escucha en '::' y acepta tanto
        conexiones IPv6 nativas como IPv4 (mapeadas como ::ffff:x.x.x.x).
        Si el sistema operativo no soporta dual-stack, cae a solo IPv4.
        La elección de protocolo la hace el cliente, no el servidor.
        """
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("::", self.port))
            print(f"[servidor] Socket dual-stack IPv4+IPv6 en puerto {self.port}")
            return sock
        except (OSError, AttributeError):
            print("[servidor] IPv6 no disponible en este sistema, usando solo IPv4")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", self.port))
            print(f"[servidor] Socket IPv4 en 0.0.0.0:{self.port}")
            return sock

    async def start(self):
        sock = self._crear_socket()

        self._server = await asyncio.start_server(
            self._on_cliente_conectado,
            sock=sock,
        )

        addr = self._server.sockets[0].getsockname()
        print(f"[servidor] Escuchando en {addr}")
        print("[servidor] Esperando clientes... (Ctrl+C para detener)")

        async with self._server:
            await self._server.serve_forever()

    async def _on_cliente_conectado(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        dispatcher = Dispatcher(self.worker_pool.executor)
        await handle_client(reader, writer, dispatcher, self.db_path)

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        self.worker_pool.shutdown()
        print("[servidor] Servidor detenido.")
