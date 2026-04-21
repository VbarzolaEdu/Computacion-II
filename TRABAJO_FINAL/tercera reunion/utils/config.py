"""
Configuración centralizada del proyecto.
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuración principal"""

    # Server
    HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("SERVER_PORT", "5000"))

    # Workers
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "4"))
    WORKER_TIMEOUT: int = int(os.getenv("WORKER_TIMEOUT", "30"))

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "./data/reservas.db")
    DB_TIMEOUT: int = int(os.getenv("DB_TIMEOUT", "10"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")

    # Features
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "100"))  # requests por minuto

    def __post_init__(self):
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
