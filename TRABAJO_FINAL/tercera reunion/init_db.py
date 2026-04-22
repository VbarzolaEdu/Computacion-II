"""
COMENTADO: Script para inicializar la base de datos.
La BD no se usa - las validaciones se hacen en memoria (data.py)
y la persistencia se hace en JSON logs (utils/reserva_logger.py)
"""
# import sqlite3
# import os
# from utils.config import Config
# from utils.logger import get_logger
#
# logger = get_logger(__name__)
#
#
# def init_database():
#     """Crea las tablas de la BD"""
#
#     config = Config()
#
#     # Crear directorio si no existe
#     os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
#
#     # Conectar
#     conn = sqlite3.connect(config.DB_PATH)
#     cursor = conn.cursor()
#
#     # Crear tabla de canchas
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS canchas (
#             id TEXT PRIMARY KEY,
#             nombre TEXT NOT NULL,
#             precio_por_hora REAL NOT NULL,
#             disponible BOOLEAN DEFAULT 1,
#             ubicacion TEXT,
#             creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#
#     # Crear tabla de reservas
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS reservas (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             cliente_id TEXT NOT NULL,
#             cancha_id TEXT NOT NULL,
#             horario TEXT NOT NULL,
#             fecha TEXT NOT NULL,
#             precio REAL NOT NULL,
#             estado TEXT DEFAULT 'confirmada',
#             creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             confirmada_en TIMESTAMP,
#             FOREIGN KEY (cancha_id) REFERENCES canchas(id)
#         )
#     """)
#
#     # Crear tabla de usuarios
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS usuarios (
#             id TEXT PRIMARY KEY,
#             nombre TEXT NOT NULL,
#             email TEXT,
#             teléfono TEXT,
#             creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#
#     # Insertar canchas de ejemplo
#     canchas_ejemplo = [
#         ("cancha_1", "Cancha A", 50.0, True, "Sector A"),
#         ("cancha_2", "Cancha B", 60.0, True, "Sector B"),
#         ("cancha_3", "Cancha C", 55.0, True, "Sector C"),
#     ]
#
#     for cancha_id, nombre, precio, disponible, ubicacion in canchas_ejemplo:
#         cursor.execute(
#             """
#             INSERT OR IGNORE INTO canchas (id, nombre, precio_por_hora, disponible, ubicacion)
#             VALUES (?, ?, ?, ?, ?)
#             """,
#             (cancha_id, nombre, precio, disponible, ubicacion)
#         )
#
#     conn.commit()
#     conn.close()
#
#     logger.info(f"✅ Base de datos inicializada en {config.DB_PATH}")
#
#
# if __name__ == "__main__":
#     init_database()
