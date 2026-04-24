import sqlite3

import data

# Horarios con multiplicador de precio.
# 18:00, 19:00, 20:00 son "horario pico" → precio * 1.2
_MULTIPLICADORES = {
    "18:00": 1.2,
    "19:00": 1.2,
    "20:00": 1.2,
}


def init_db(db_path: str):
    """
    Crea las tablas y carga los datos iniciales si no existen.

    Se llama una sola vez en main.py antes de arrancar el servidor.
    Usa CREATE TABLE IF NOT EXISTS e INSERT OR IGNORE para ser idempotente:
    se puede llamar múltiples veces sin borrar datos existentes.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    _crear_tablas(conn)
    _seed_clubes(conn)
    _seed_canchas(conn)
    _seed_horarios(conn)

    conn.commit()
    conn.close()
    print(f"[db] Base de datos lista: {db_path}")


def _crear_tablas(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clubes (
            id        TEXT PRIMARY KEY,
            nombre    TEXT NOT NULL,
            direccion TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS canchas (
            id          TEXT PRIMARY KEY,
            club_id     TEXT NOT NULL,
            nombre      TEXT NOT NULL,
            tipo        TEXT NOT NULL,
            precio_base INTEGER NOT NULL,

            FOREIGN KEY (club_id) REFERENCES clubes(id)
        );

        CREATE TABLE IF NOT EXISTS horarios (
            horario       TEXT PRIMARY KEY,
            multiplicador REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reservas (
            id           TEXT PRIMARY KEY,
            cliente_id   TEXT NOT NULL,
            nombre       TEXT NOT NULL,
            cancha_id    TEXT NOT NULL,
            fecha        TEXT NOT NULL,
            horario      TEXT NOT NULL,
            precio_final REAL NOT NULL,
            creada_en    TEXT NOT NULL,

            FOREIGN KEY (cancha_id) REFERENCES canchas(id),
            FOREIGN KEY (horario)   REFERENCES horarios(horario),
            UNIQUE(cancha_id, fecha, horario)
        );
    """)


def _seed_clubes(conn: sqlite3.Connection):
    for club_id, info in data.CLUBES.items():
        conn.execute(
            "INSERT OR IGNORE INTO clubes (id, nombre, direccion) VALUES (?, ?, ?)",
            (club_id, info["nombre"], info["direccion"]),
        )


def _seed_canchas(conn: sqlite3.Connection):
    for cancha_id, info in data.CANCHAS.items():
        conn.execute(
            "INSERT OR IGNORE INTO canchas (id, club_id, nombre, tipo, precio_base) VALUES (?, ?, ?, ?, ?)",
            (cancha_id, info["club_id"], info["nombre"], info["tipo"], info["precio_por_hora"]),
        )


def _seed_horarios(conn: sqlite3.Connection):
    for horario in data.HORARIOS_DISPONIBLES:
        multiplicador = _MULTIPLICADORES.get(horario, 1.0)
        conn.execute(
            "INSERT OR IGNORE INTO horarios (horario, multiplicador) VALUES (?, ?)",
            (horario, multiplicador),
        )
