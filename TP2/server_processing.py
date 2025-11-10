# server_processing.py
import socketserver
import json
from multiprocessing import Pool, cpu_count
from processor.screenshot import take_screenshot
from processor.performance import analyze_performance
from processor.image_processor import process_images

# --- Función principal que combina todas las tareas ---
def handle_task(task: dict) -> dict:
    url = task.get("url")
    print(f"[+] Procesando tarea para: {url}")

    screenshot = take_screenshot(url)
    performance = analyze_performance(url)
    thumbnails = process_images(url)

    result = {
        "screenshot": screenshot,
        "performance": performance,
        "thumbnails": thumbnails
    }
    return result


# --- Clase que maneja cada conexión entrante ---
class ProcessingHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(4096).decode()
            task = json.loads(data)
            print(f"[📨] Tarea recibida: {task}")

            # Procesar usando multiprocessing
            with Pool(cpu_count()) as pool:
                result = pool.apply(handle_task, (task,))

            # Enviar resultado al servidor A
            response = json.dumps(result).encode()
            self.request.sendall(response)
            print(f"[✓] Tarea completada para {task['url']}")
        except Exception as e:
            print(f"[❌] Error al manejar la tarea: {e}")
            self.request.sendall(json.dumps({"error": str(e)}).encode())


# --- Punto de entrada ---
if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 9000
    with socketserver.TCPServer((HOST, PORT), ProcessingHandler) as server:
        print(f"🧠 Servidor de procesamiento corriendo en {HOST}:{PORT}")
        server.serve_forever()
