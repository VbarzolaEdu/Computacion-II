"""
Orquestador de workers: gestión centralizada de ProcessPoolExecutor.
Responsable de crear, configurar y cerrar el pool de workers.
Las tareas en sí se definen en tasks.py
"""
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class WorkerPool:
    """Orquestador del pool de workers - responsable de su ciclo de vida"""

    def __init__(self, num_workers: int = 4):
        """
        Inicializa el gestor del pool.

        Args:
            num_workers: Número de workers en el pool (default: 4)
        """
        self.num_workers = num_workers
        self.executor: Optional[ProcessPoolExecutor] = None

    def create(self):
        """Crea e inicializa el pool de workers"""
        self.executor = ProcessPoolExecutor(
            max_workers=self.num_workers,
            initializer=self._init_worker
        )
        logger.info(f"✓ Pool de {self.num_workers} workers creado")

    def shutdown(self, wait: bool = True):
        """
        Cierra el pool de workers de forma ordenada.

        Args:
            wait: Si True, espera a que terminen todos los workers
        """
        if self.executor:
            self.executor.shutdown(wait=wait)
            logger.info("✓ Pool de workers cerrado")

    @staticmethod
    def _init_worker():
        """
        Inicializador que se ejecuta UNA SOLA VEZ por worker.
        Se ejecuta en el contexto del worker (proceso separado).
        Útil para inicializar logging, conexiones, etc. por worker.
        """
        logger.info("Worker inicializado en proceso separado")
