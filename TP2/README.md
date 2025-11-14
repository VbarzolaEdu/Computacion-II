# TP2 – Sistema de Scraping y Análisis Web Distribuido

## Descripción

Sistema distribuido de scraping web implementado en Python que coordina dos servidores:

- **Servidor A (server_scraping.py)**: Servidor HTTP asíncrono con `aiohttp` que recibe requests, descarga HTML y extrae metadatos usando `BeautifulSoup`.
- **Servidor B (server_processing.py)**: Servidor TCP con pool de workers (`multiprocessing`) que procesa tareas CPU-intensivas: capturas de pantalla con `Playwright` y análisis de rendimiento.

El cliente interactúa solo con el Servidor A mediante HTTP GET. El Servidor A coordina con el Servidor B vía sockets TCP usando un protocolo binario personalizado (longitud + JSON).

---

## Arquitectura

```
Cliente  →  HTTP GET /scrape?url=...
              ↓
        Servidor A (asyncio + aiohttp)
          - Descarga HTML
          - Parse con BeautifulSoup
          - Extrae metadatos
              ↓
          Socket TCP
              ↓
        Servidor B (multiprocessing)
          - Screenshot (Playwright)
          - Análisis de performance
              ↓
        Respuesta JSON consolidada
```

**Flujo:**
1. Cliente solicita scraping de una URL al Servidor A (endpoint `/scrape?url=...`).
2. Servidor A descarga el HTML de forma asíncrona con `aiohttp`.
3. Servidor A parsea el HTML con `BeautifulSoup` y extrae: título, links, metadatos, estructura de headers, cantidad de imágenes.
4. Servidor A envía los datos al Servidor B mediante socket TCP.
5. Servidor B ejecuta en paralelo (pool de workers): captura de pantalla con Playwright y análisis de rendimiento (tiempo de carga, tamaño total, número de requests).
6. Servidor B responde al Servidor A con los resultados procesados.
7. Servidor A devuelve al cliente un JSON con scraping + processing.

---

## Requisitos

- Python 3.10+
- Dependencias listadas en `requirements.txt`:
  - `aiohttp`
  - `beautifulsoup4`
  - `lxml`
  - `playwright`
  - `requests`
  - `pytest`

---

## Instalación

```bash
cd TP2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install  # Descarga navegadores (Chromium)
```

---

## Ejecución

### 1. Iniciar Servidor B (procesamiento)

En una terminal:
```bash
python3 server_processing.py --ip :: --port 9000 --workers 4
```

**Parámetros:**
- `--ip`: Dirección IP (por defecto `::` para dual-stack IPv4/IPv6)
- `--port`: Puerto TCP (por defecto `9000`)
- `--workers`: Número de procesos workers (por defecto `4`)

### 2. Iniciar Servidor A (scraping)

En otra terminal:
```bash
python3 server_scraping.py --ip :: --port 8000 --b_ip ::1 --b_port 9000
```

**Parámetros:**
- `--ip`: IP del servidor HTTP (por defecto `::`)
- `--port`: Puerto HTTP (por defecto `8000`)
- `--b_ip`: IP del Servidor B (por defecto `::1`)
- `--b_port`: Puerto del Servidor B (por defecto `9000`)

### 3. Ejecutar cliente

En una tercera terminal:
```bash
python3 client.py
```

Ingresa una URL cuando se solicite (ejemplo: `https://example.com`).

### 4. Probar con curl

```bash
curl "http://127.0.0.1:8000/scrape?url=https://example.com"
```

Respuesta JSON (ejemplo):
```json
{
  "url": "https://example.com",
  "scraping_data": {
    "title": "Example Domain",
    "links": ["https://www.iana.org/domains/example"],
    "meta_tags": {"description": "Example domain..."},
    "structure": {"h1": 1, "h2": 0, ...},
    "images_count": 0
  },
  "processing_data": {
    "screenshot": "iVBORw0KGgoAAAA...",
    "performance": {
      "load_time_ms": 156,
      "total_size_kb": 1.23,
      "num_requests": 3
    },
    "status": "ok"
  },
  "status": "success"
}
```

---

## Testing

Ejecutar tests con `pytest`:

```bash
python -m pytest -v
```

Ejecutar tests específicos:
```bash
python -m pytest -v tests/test_processor.py
python -m pytest -v tests/test_scraper.py
```

---

## Estructura del proyecto

```
TP2/
├── server_scraping.py           # Servidor A (asyncio + aiohttp)
├── server_processing.py         # Servidor B (multiprocessing + TCP)
├── client.py                    # Cliente HTTP de prueba
├── requirements.txt             # Dependencias
├── README.md                    # Este archivo
├── .gitignore
│
├── common/
│   ├── protocol.py              # Funciones de logging
│   └── serialization.py         # Envío/recepción de mensajes JSON por socket
│
├── scraper/
│   ├── html_parser.py           # Parse HTML con BeautifulSoup
│   └── metadata_extractor.py   # Extrae meta tags (Open Graph, Twitter Cards)
│
├── processor/
│   ├── screenshot.py            # Captura con Playwright
│   └── performance.py           # Análisis de rendimiento (tiempo, tamaño, requests)
│
└── tests/
    ├── test_processor.py        # Tests de screenshot y performance
    └── test_scraper.py          # Tests de scraping
```

---

## Autor

Valentin Barzola  
Universidad de Mendoza – Computación II  
2025
