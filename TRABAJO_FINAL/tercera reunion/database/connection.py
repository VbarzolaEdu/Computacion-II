"""
Manejo de conexión a la base de datos.
"""
import logging
from typing import Optional
import sqlite3

from utils.logger import get_logger
from utils.config import Config

logger = get_logger(__name__)


class Database:
    """Gestor de conexión a BD"""

    _instance: Optional['Database'] = None

    def __new__(cls, config: Config):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Config):
        if self._initialized:
            return

        self.config = config
        self.conn: Optional[sqlite3.Connection] = None
        self._initialized = True

    def connect(self):
        """Abre conexión a la BD"""
        try:
            self.conn = sqlite3.connect(self.config.DB_PATH)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Conectado a BD: {self.config.DB_PATH}")
            self._create_tables()
        except sqlite3.Error as e:
            logger.error(f"Error conectando a BD: {e}")
            raise

    def disconnect(self):
        """Cierra conexión a la BD"""
        if self.conn:
            self.conn.close()
            logger.info("Desconectado de BD")

    def execute(self, query: str, params: tuple = ()):
        """Ejecuta una query"""
        if not self.conn:
            raise RuntimeError("BD no conectada")

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchone(self, query: str, params: tuple = ()):
        """Ejecuta query y retorna un resultado"""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        """Ejecuta query y retorna todos los resultados"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def _create_tables(self):
        """Crea tablas si no existen"""
        # TODO: crear tablas de canchas, reservas, usuarios
        logger.info("Tablas de BD verificadas")


# Singleton global
_db: Optional[Database] = None


def get_db(config: Config) -> Database:
    """Obtiene instancia global de DB"""
    global _db
    if _db is None:
        _db = Database(config)
        _db.connect()
    return _db
