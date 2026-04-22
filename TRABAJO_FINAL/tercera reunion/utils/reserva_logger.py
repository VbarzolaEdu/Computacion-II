"""
Logger especializado para registrar reservas en formato JSON.
Escribe cada reserva confirmada en un archivo JSONL (JSON Lines).
"""
import json
import os
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
import threading

from utils.config import Config


class ReservaLogger:
    """Logger que escribe reservas confirmadas en formato JSON (JSONL)"""

    def __init__(self, log_file: str = None):
        """
        Inicializa el logger de reservas.

        Args:
            log_file: Ruta del archivo de logs. Si no se especifica,
                      usa la configuración por defecto.
        """
        if log_file is None:
            config = Config()
            # Usar el mismo directorio que los logs generales
            logs_dir = os.path.dirname(config.LOG_FILE)
            log_file = os.path.join(logs_dir, "reservas.jsonl")

        self.log_file = log_file
        self._lock = threading.Lock()

        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_reserva_confirmada(self, reserva_data: Dict[str, Any]) -> None:
        """
        Registra una reserva confirmada en el archivo JSON Lines.

        Args:
            reserva_data: Diccionario con los datos de la reserva
        """
        try:
            # Preparar el registro con timestamp
            registro = {
                "timestamp": datetime.now().isoformat(),
                "tipo": "reserva_confirmada",
                "datos": reserva_data
            }

            # Thread-safe: usar lock para evitar conflictos entre threads
            with self._lock:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")

        except Exception as e:
            # Si falla el logging, no debe afectar el flujo de la aplicación
            # pero sí loguear el error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al registrar reserva en JSON: {e}")

    def log_reserva_rechazada(self, reserva_data: Dict[str, Any], razon: str) -> None:
        """
        Registra una reserva rechazada.

        Args:
            reserva_data: Diccionario con los datos de la reserva
            razon: Motivo del rechazo
        """
        try:
            registro = {
                "timestamp": datetime.now().isoformat(),
                "tipo": "reserva_rechazada",
                "razon": razon,
                "datos": reserva_data
            }

            with self._lock:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al registrar rechazo en JSON: {e}")


# Instancia global del logger
_reserva_logger_instance = None


def get_reserva_logger() -> ReservaLogger:
    """Obtiene la instancia global del logger de reservas"""
    global _reserva_logger_instance
    if _reserva_logger_instance is None:
        _reserva_logger_instance = ReservaLogger()
    return _reserva_logger_instance
