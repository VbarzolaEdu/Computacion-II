import datetime
import json
import socket

# --- Función para registrar errores ---
def log_error(message: str):
    """
    Registra errores con fecha y hora en un archivo de log
    y los imprime en consola.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] ERROR: {message}"
    print(formatted)
    try:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        # No interrumpe el flujo si no se puede escribir el log
        pass


# --- Comunicación segura entre servidores (A → B) ---
def safe_socket_request(data: dict, host: str = "127.0.0.1", port: int = 9000, timeout: int = 10):
    """
    Envía datos por socket al servidor de procesamiento (B)
    y maneja errores comunes de red.
    """
    serialized = json.dumps(data).encode()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendall(serialized)
            response = s.recv(65536)
            return json.loads(response)
    except (ConnectionRefusedError, socket.timeout):
        log_error(f"Servidor B no disponible o timeout (host={host}, port={port})")
        return {"error": "processing_server_unavailable"}
    except json.JSONDecodeError:
        log_error("Respuesta inválida recibida del servidor B.")
        return {"error": "invalid_response"}
    except Exception as e:
        log_error(f"Error inesperado en comunicación socket: {e}")
        return {"error": str(e)}
