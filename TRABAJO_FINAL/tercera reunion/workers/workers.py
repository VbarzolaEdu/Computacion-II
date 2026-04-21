"""
Pool de workers: gestión de ProcessPoolExecutor.
Nota: los workers en sí se definen en tasks.py
"""
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class WorkerPool:
    """Gestor del pool de workers"""


//Esta hardcodedado en numero
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.executor: Optional[ProcessPoolExecutor] = None

    def create(self):
        """Crea el pool"""
        self.executor = ProcessPoolExecutor(
            max_workers=self.num_workers,
            initializer=self._init_worker
        )
        logger.info(f"Pool de {self.num_workers} workers creado")

    def shutdown(self, wait: bool = True):
        """Cierra el pool"""
        if self.executor:
            self.executor.shutdown(wait=wait)
            logger.info("Pool de workers cerrado")

    @staticmethod
    def _init_worker():
        """Inicializador para cada worker"""
        # Aquí se ejecuta UNA SOLA VEZ por worker
        # Útil para inicializar DB connections, logging, etc.
        logger.info(f"Worker inicializado")
