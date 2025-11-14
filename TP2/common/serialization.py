# common/serialization.py
import json
import socket
from common.protocol import log_error

def to_json(data: dict) -> bytes:
    """
    Serializa un diccionario Python a JSON en formato bytes.
    """
    try:
        return json.dumps(data).encode("utf-8")
    except Exception as e:
        log_error(f"Error serializando JSON: {e}")
        return b'{}'


def from_json(data: bytes) -> dict:
    """
    Deserializa bytes a un diccionario Python.
    """
    try:
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        log_error(f"Error deserializando JSON: {e}")
        return {"error": "invalid_json"}


def send_packet(sock: socket.socket, data: dict):
    """
    Envía un mensaje JSON con protocolo:
        [4 bytes: longitud][payload JSON]
    """
    try:
        payload = to_json(data)
        size = len(payload).to_bytes(4, "big")
        sock.sendall(size + payload)
    except Exception as e:
        log_error(f"Error enviando paquete: {e}")


def recv_packet(sock: socket.socket) -> dict:
    """
    Recibe un paquete usando protocolo:
        [4 bytes: longitud][payload JSON]
    """
    try:
        size_data = sock.recv(4)
        if not size_data:
            return {"error": "empty_size"}

        length = int.from_bytes(size_data, "big")
        payload = sock.recv(length)

        return from_json(payload)

    except Exception as e:
        log_error(f"Error recibiendo paquete: {e}")
        return {"error": "receive_failed"}
