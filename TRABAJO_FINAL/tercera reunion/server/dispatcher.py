"""
Dispatcher: asigna tareas del pool de workers.
Coordina entre asyncio (concurrencia) y workers (paralelismo).
"""
import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict

from utils.logger import get_logger
from workers.tasks import procesar_reserva
from models.schemas import ReservaRequest

logger = get_logger(__name__)


class Dispatcher:
    """Dispatcher que maneja la asignación de tareas a workers"""

    def __init__(self, executor: ProcessPoolExecutor):
        self.executor = executor
        self.pending_tasks: Dict[str, asyncio.Task] = {}

    async def dispatch(self, request_id: str, request: ReservaRequest) -> Dict[str, Any]:
        """
        Despacha una tarea al pool de workers.

        Usa run_in_executor para no bloquear el event loop.
        """
        logger.info(f"Despachando request {request_id}")

        # Obtener el event loop actual
        loop = asyncio.get_event_loop()

        try:
            # Ejecutar en executor (worker) sin bloquear asyncio
            result = await loop.run_in_executor(
                self.executor,
                procesar_reserva,
                request.dict()
            )

            logger.info(f"Request {request_id} completada: {result}")
            return result

        except Exception as e:
            logger.error(f"Error en dispatcher para {request_id}: {e}")
            raise

    async def shutdown(self):
        """Cierra todos los pending tasks"""
        for request_id, task in self.pending_tasks.items():
            if not task.done():
                task.cancel()

        # Esperar a que se completen
        if self.pending_tasks:
            await asyncio.gather(*self.pending_tasks.values(), return_exceptions=True)
