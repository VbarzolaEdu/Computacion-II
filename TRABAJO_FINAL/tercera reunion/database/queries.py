"""
COMENTADO: Consultas a la base de datos.
La BD no se usa - las validaciones se hacen en memoria (data.py)
y la persistencia se hace en JSON logs (utils/reserva_logger.py)
"""
# import logging
# from typing import Any, Dict
# from datetime import datetime
#
# from utils.logger import get_logger
# from utils.config import Config
# from database.connection import get_db
#
# logger = get_logger(__name__)
#
#
# def guardar_reserva(request_dict: Dict[str, Any]) -> str:
#     """
#     Guarda una reserva en la BD.
#     Retorna el ID de la reserva guardada.
#     """
#     config = Config()
#     db = get_db(config)
#
#     query = """
#     INSERT INTO reservas (cliente_id, cancha_id, horario, fecha, precio, estado, creada_en)
#     VALUES (?, ?, ?, ?, ?, 'confirmada', ?)
#     """
#
#     params = (
#         request_dict.get("cliente_id"),
#         request_dict.get("cancha_id"),
#         request_dict.get("horario"),
#         request_dict.get("fecha"),
#         request_dict.get("precio"),
#         datetime.now().isoformat()
#     )
#
#     try:
#         cursor = db.execute(query, params)
#         reserva_id = cursor.lastrowid
#         logger.info(f"Reserva guardada con ID: {reserva_id}")
#         return str(reserva_id)
#     except Exception as e:
#         logger.error(f"Error guardando reserva: {e}")
#         raise
#
#
# def obtener_reserva(reserva_id: str) -> Dict[str, Any]:
#     """Obtiene una reserva por ID"""
#     config = Config()
#     db = get_db(config)
#
#     query = "SELECT * FROM reservas WHERE id = ?"
#     row = db.fetchone(query, (reserva_id,))
#
#     if row:
#         return dict(row)
#     return None
#
#
# def obtener_reservas_cliente(cliente_id: str) -> list:
#     """Obtiene todas las reservas de un cliente"""
#     config = Config()
#     db = get_db(config)
#
#     query = "SELECT * FROM reservas WHERE cliente_id = ? ORDER BY creada_en DESC"
#     rows = db.fetchall(query, (cliente_id,))
#
#     return [dict(row) for row in rows]
#
#
# def verificar_disponibilidad(cancha_id: str, horario: str, fecha: str) -> bool:
#     """Verifica si una cancha está disponible en un horario"""
#     config = Config()
#     db = get_db(config)
#
#     query = """
#     SELECT COUNT(*) as count FROM reservas
#     WHERE cancha_id = ? AND horario = ? AND fecha = ? AND estado = 'confirmada'
#     """
#
#     row = db.fetchone(query, (cancha_id, horario, fecha))
#     count = row[0] if row else 0
#
#     return count == 0
