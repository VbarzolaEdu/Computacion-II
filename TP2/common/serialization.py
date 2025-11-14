import json
import socket
from common.protocol import log_error

def to_json(data: dict) -> bytes:
    """
    Serializa un diccionario Python a JSON en formato bytes.
    """
    try:
        return json.dumps(data).encode('utf-8')
    except Exception as e:
        log_error(f"Error serializando JSON: {e}")
        return b'{}'


def from_json(data: bytes) -> dict:
    """
    Deserializa bytes en un diccionario Python.
    """
    try:
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        log_error(f"Error deserializando JSON: {e}")
        return {"error": "invalid_json"}


def send_json(sock: socket.socket, data: dict):
    """
    Envía un JSON serializado por un socket TCP.
    """
    try:
        sock.sendall(to_json(data))
    except Exception as e:
        log_error(f"Error enviando datos por socket: {e}")


def recv_json(sock: socket.socket, buffer_size: int = 65536) -> dict:
    """
    Recibe datos JSON desde un socket y los deserializa.
    """
    try:
        raw = sock.recv(buffer_size)
        return from_json(raw)
    except Exception as e:
        log_error(f"Error recibiendo datos por socket: {e}")
        return {"error": "receive_failed"}

