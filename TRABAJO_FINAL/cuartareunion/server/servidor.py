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
        self._servers: list[asyncio.Server] = []

    def _crear_sockets(self) -> list[socket.socket]:
        """
        Usa AF_UNSPEC + AI_PASSIVE en getaddrinfo para obtener las direcciones
        de todas las familias disponibles (IPv4 y IPv6) y crea un socket real
        e independiente por cada familia.

        A diferencia del enfoque dual-stack con IPV6_V6ONLY=0, aquí IPv4 e
        IPv6 tienen su propio socket: no hay conversión ::ffff:x.x.x.x.
        """
        sockets = []
        vistas = set()

        try:
            infos = socket.getaddrinfo(
                None, self.port,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM,
                0,
                socket.AI_PASSIVE,
            )
        except socket.gaierror as exc:
            print(f"[servidor] getaddrinfo falló ({exc}), usando solo IPv4")
            infos = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("0.0.0.0", self.port))]

        for family, socktype, proto, _canonname, sockaddr in infos:
            if family in vistas:
                continue
            vistas.add(family)

            try:
                sock = socket.socket(family, socktype, proto)
                if family == socket.AF_INET6:
                    # IPV6_V6ONLY=1: este socket solo acepta IPv6 nativo,
                    # no IPv4 mapeado — eso lo maneja el socket AF_INET.
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(sockaddr)
                nombre = "IPv6" if family == socket.AF_INET6 else "IPv4"
                print(f"[servidor] Socket {nombre} enlazado en {sockaddr}")
                sockets.append(sock)
            except OSError as exc:
                print(f"[servidor] No se pudo crear socket {family.name}: {exc}")

        return sockets

    async def start(self):
        sockets = self._crear_sockets()
        if not sockets:
            raise RuntimeError("No se pudo crear ningún socket de escucha")

        for sock in sockets:
            server = await asyncio.start_server(
                self._on_cliente_conectado,
                sock=sock,
            )
            self._servers.append(server)
            addr = server.sockets[0].getsockname()
            print(f"[servidor] Escuchando en {addr}")

        print("[servidor] Esperando clientes... (Ctrl+C para detener)")

        async with asyncio.TaskGroup() as tg:
            for server in self._servers:
                tg.create_task(server.serve_forever())

    async def _on_cliente_conectado(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        dispatcher = Dispatcher(self.worker_pool.executor)
        await handle_client(reader, writer, dispatcher, self.db_path)

    async def stop(self):
        for server in self._servers:
            server.close()
        for server in self._servers:
            await server.wait_closed()
        self._servers.clear()
        self.worker_pool.shutdown()
        print("[servidor] Servidor detenido.")
