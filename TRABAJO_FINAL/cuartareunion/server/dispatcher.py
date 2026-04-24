import asyncio
from concurrent.futures import ProcessPoolExecutor

from workers.tasks import procesar_reserva


class Dispatcher:
    """
    Puente entre el mundo asyncio (I/O-bound) y el pool de workers (CPU-bound).

    El servidor asyncio vive en un único hilo y no puede ejecutar código
    bloqueante. Cuando llega una reserva, el Dispatcher usa run_in_executor()
    para delegar la tarea a un worker del ProcessPoolExecutor.

    run_in_executor() hace dos cosas:
      - Envía la función al pool (otro proceso)
      - Devuelve un Future que asyncio puede 'await', liberando el event loop
        para atender otros clientes mientras el worker trabaja
    """

    def __init__(self, executor: ProcessPoolExecutor):
        self.executor = executor

    async def dispatch(self, request_id: str, request_dict: dict) -> dict:
        loop = asyncio.get_event_loop()

        print(f"[dispatcher] Enviando {request_id} al pool de workers")

        # run_in_executor toma una función SINCRÓNICA y la ejecuta en el pool.
        # No puede recibir kwargs, solo args posicionales.
        resultado = await loop.run_in_executor(
            self.executor,
            procesar_reserva,
            request_dict,
        )

        print(f"[dispatcher] Resultado de {request_id}: {resultado['estado']}")
        return resultado
