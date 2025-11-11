import socketserver
import json
from multiprocessing import Pool, cpu_count
from processor.screenshot import take_screenshot
from processor.performance import analyze_performance
from processor.image_processor import process_images
from common.protocol import log_error


def handle_task(task: dict) -> dict:
    url = task.get("url", "")
    try:
        print(f"[+] Procesando tarea para: {url}")
        screenshot = take_screenshot(url)
        performance = analyze_performance(url)
        thumbnails = process_images(url)
        return {
            "screenshot": screenshot,
            "performance": performance,
            "thumbnails": thumbnails,
            "status": "ok"
        }
    except Exception as e:
        log_error(f"Error procesando {url}: {e}")
        return {"error": str(e), "status": "failed"}


class ProcessingHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(8192).decode()
            task = json.loads(data)

            with Pool(cpu_count()) as pool:
                result = pool.apply(handle_task, (task,))

            self.request.sendall(json.dumps(result).encode())
        except json.JSONDecodeError:
            log_error("Datos inválidos recibidos por socket.")
            self.request.sendall(json.dumps({"error": "invalid_json"}).encode())
        except Exception as e:
            log_error(f"Error general en handler: {e}")
            self.request.sendall(json.dumps({"error": str(e)}).encode())


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 9000
    with socketserver.TCPServer((HOST, PORT), ProcessingHandler) as server:
        print(f"🧠 Servidor de procesamiento corriendo en {HOST}:{PORT}")
        server.serve_forever()
