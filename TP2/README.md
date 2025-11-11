# 🧠 TP2 – Sistema de Scraping y Análisis Web Distribuido

## 📋 Descripción general

Este proyecto implementa un **sistema distribuido de scraping y análisis web** utilizando **Python**, **asyncio**, y **multiprocessing**.  
El sistema está compuesto por **dos servidores** que trabajan de forma coordinada:

- **Servidor A (Asyncio)** → recibe solicitudes HTTP, realiza scraping de páginas web de forma asíncrona y coordina el flujo de información.  
- **Servidor B (Multiprocessing)** → procesa tareas pesadas en paralelo (screenshots, análisis de rendimiento e imágenes).  

El cliente solo interactúa con el **Servidor A**, que devuelve una respuesta JSON consolidada con toda la información extraída y procesada.

---

## ⚙️ Arquitectura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ HTTP POST /scrape
       ▼
┌──────────────────────────────────────────────┐
│         Servidor A (Asyncio)                 │
│  - Recibe requests del cliente               │
│  - Scraping HTML asíncrono (aiohttp)         │
│  - Extracción de metadatos (BeautifulSoup)   │
│  - Comunica con Servidor B para tareas CPU   │
└──────────────┬───────────────────────────────┘
               │ Socket TCP
               ▼
┌──────────────────────────────────────────────┐
│      Servidor B (Multiprocessing)            │
│  - Pool de workers (procesos)                │
│  - Screenshots (Playwright)                  │
│  - Análisis de rendimiento                   │
│  - Procesamiento de imágenes (Pillow)        │
└──────────────────────────────────────────────┘
```

**Flujo de trabajo:**
1. Cliente envía solicitud HTTP POST con la URL a scrapear.
2. Servidor A realiza el scraping HTML y extrae metadatos.
3. Servidor A envía tareas al Servidor B (screenshot, performance, imágenes).
4. Servidor B procesa las tareas en paralelo usando workers.
5. Servidor A recibe las respuestas del Servidor B y consolida el resultado final.
6. Servidor A devuelve al cliente un JSON con todos los datos.

---

## 🧩 Funcionalidades principales

| Funcionalidad | Descripción |
|----------------|-------------|
| **Scraping HTML** | Descarga de páginas web usando `aiohttp` y `asyncio`. |
| **Extracción de metadatos** | Obtiene título, meta tags, headers, links e imágenes. |
| **Generación de screenshot** | Usa `Playwright` (Chromium headless) para capturar la página. |
| **Análisis de rendimiento** | Mide tiempo de carga y tamaño total de recursos. |
| **Procesamiento de imágenes** | Descarga y genera thumbnails con `Pillow`. |
| **Manejo de errores avanzado** | Control de fallos de red, timeouts, JSON inválido, etc. |
| **CLI configurable** | Ejecución parametrizada con `argparse` (`-i`, `-p`, `-w`, `-n`). |
| **Testing automatizado** | Pruebas unitarias e integración con `pytest` y `pytest-asyncio`. |

---

## 📦 Requisitos

### 🐍 Python
Versión recomendada: **Python 3.10 o superior**

### 📚 Dependencias
Instalar con:
```bash
pip install -r requirements.txt
```

**Paquetes incluidos:**
- `aiohttp` → HTTP cliente asíncrono para scraping
- `beautifulsoup4` + `lxml` → Parsing y extracción de HTML
- `playwright` → Automatización de navegadores (screenshots)
- `pillow` → Procesamiento de imágenes
- `requests` → HTTP cliente síncrono
- `pytest` + `pytest-asyncio` → Testing

**Instalación de navegadores Playwright:**
```bash
playwright install
```
Esto descarga Chromium, Firefox y WebKit. Solo se usa Chromium por defecto.

---

## 🚀 Instalación y configuración

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/VbarzolaEdu/Computacion-II.git
cd Computacion-II/TP2
```

### 2️⃣ Crear entorno virtual (recomendado)
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3️⃣ Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install  # Descarga navegadores para Playwright
```

### 4️⃣ Verificar instalación
```bash
python3 --version  # Debe ser 3.10+
pip list  # Verificar que todas las dependencias estén instaladas
```

---

## 🏃 Ejecución

### Paso 1: Iniciar el Servidor B (Procesamiento)
En una terminal:
```bash
cd TP2
source .venv/bin/activate  # Si usas entorno virtual
python3 server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

**Parámetros:**
- `-i` / `--ip`: IP del servidor (por defecto: `127.0.0.1`)
- `-p` / `--port`: Puerto TCP (por defecto: `9000`)
- `-n` / `--num-workers`: Número de workers/procesos (por defecto: `4`)

**Salida esperada:**
```
[INFO] Servidor de procesamiento iniciado en 127.0.0.1:9000
[INFO] Pool de 4 workers creado
```

### Paso 2: Iniciar el Servidor A (Scraping)
En otra terminal:
```bash
cd TP2
source .venv/bin/activate
python3 server_scraping.py -i 127.0.0.1 -p 8000 -w 4
```

**Parámetros:**
- `-i` / `--ip`: IP del servidor HTTP (por defecto: `127.0.0.1`)
- `-p` / `--port`: Puerto HTTP (por defecto: `8000`)
- `-w` / `--workers`: Número de workers asyncio (por defecto: `4`)

**Salida esperada:**
```
[INFO] Servidor de scraping iniciado en http://127.0.0.1:8000
[INFO] Conectado al servidor de procesamiento en 127.0.0.1:9000
```

### Paso 3: Ejecutar el cliente
En una tercera terminal:
```bash
cd TP2
source .venv/bin/activate
python3 client.py
```

**Ejemplo de uso interactivo:**
```
Ingrese la URL a scrapear: https://example.com
```

**Respuesta JSON (ejemplo simplificado):**
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "meta": {
    "description": "Example domain for illustrative examples",
    "charset": "UTF-8"
  },
  "headers": {
    "content-type": "text/html",
    "server": "nginx"
  },
  "links": ["https://www.iana.org/domains/example"],
  "images": ["https://example.com/image.png"],
  "screenshot": "iVBORw0KGgoAAAANSUhEUg...",
  "performance": {
    "load_time_ms": 234,
    "total_size_kb": 1270,
    "num_requests": 8
  },
  "thumbnails": ["data:image/png;base64,..."]
}
```

---

## 🧪 Testing

### Ejecutar todos los tests
```bash
cd TP2
source .venv/bin/activate  # Si usas entorno virtual
python -m pytest -v
```

### Ejecutar tests específicos
```bash
# Solo tests del procesador
python -m pytest -v tests/test_processor.py

# Solo tests del scraper
python -m pytest -v tests/test_scraper.py

# Test específico
python -m pytest -v tests/test_processor.py::test_take_screenshot_returns_base64
```

### Cobertura de tests (opcional)
```bash
pip install pytest-cov
python -m pytest --cov=. --cov-report=html
```
Los resultados se generan en `htmlcov/index.html`.

**Tests incluidos:**
- ✅ Validación de estructura de respuestas
- ✅ Manejo de errores (timeouts, URLs inválidas)
- ✅ Procesamiento de imágenes
- ✅ Screenshots con Playwright
- ✅ Análisis de performance

---

## 📁 Estructura del proyecto

```
TP2/
├── client.py                    # Cliente HTTP para probar el sistema
├── server_scraping.py           # Servidor A (asyncio + HTTP)
├── server_processing.py         # Servidor B (multiprocessing)
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Este archivo
├── .gitignore                   # Archivos ignorados por git
│
├── common/                      # Módulos compartidos
│   ├── __init__.py
│   ├── protocol.py              # Protocolo de comunicación entre servidores
│   └── serialization.py         # Serialización/deserialización de mensajes
│
├── scraper/                     # Módulos de scraping
│   ├── __init__.py
│   ├── async_http.py            # Cliente HTTP asíncrono
│   ├── html_parser.py           # Parser HTML con BeautifulSoup
│   └── metadata_extractor.py   # Extracción de metadatos
│
├── processor/                   # Módulos de procesamiento
│   ├── __init__.py
│   ├── screenshot.py            # Generación de screenshots (Playwright)
│   ├── performance.py           # Análisis de rendimiento
│   └── image_processor.py       # Procesamiento de imágenes (thumbnails)
│
├── tests/                       # Tests automatizados
│   ├── test_scraper.py          # Tests del módulo scraper
│   └── test_processor.py        # Tests del módulo processor
│
└── venv/                        # Entorno virtual (no trackeado en git)
```

---

## 🔧 Configuración avanzada

### Variables de entorno (opcional)
Puedes crear un archivo `.env` para configurar parámetros por defecto:
```bash
# .env
SCRAPER_HOST=0.0.0.0
SCRAPER_PORT=8000
PROCESSOR_HOST=127.0.0.1
PROCESSOR_PORT=9000
NUM_WORKERS=4
```

### Aumentar límite de workers
Para sitios con muchas imágenes/recursos:
```bash
python3 server_processing.py -n 8  # Aumentar a 8 workers
```

### Timeout personalizado
Editar constantes en `scraper/async_http.py` o `processor/screenshot.py`:
```python
TIMEOUT = 30  # segundos
```

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'processor'`
**Solución:** Ejecutar desde el directorio `TP2/`:
```bash
cd TP2
python3 server_scraping.py
```

### Error: `playwright: command not found` o `Browser not found`
**Solución:** Instalar navegadores de Playwright:
```bash
playwright install
```

### Error: `Address already in use`
**Solución:** El puerto está ocupado. Cambia el puerto o mata el proceso:
```bash
# Ver procesos usando el puerto 8000
lsof -i :8000
# Matar el proceso
kill -9 <PID>
```

### Tests fallan con timeout
**Solución:** Algunos tests requieren conexión a internet. Verifica tu red o aumenta el timeout en los tests.

### `pip install -r requirements.txt` falla
**Solución:** Asegúrate de que `requirements.txt` no contenga líneas inválidas como `common.errors` (ya fue corregido).

---

## 📝 Notas adicionales

- **Desactivar entorno virtual:** `deactivate`
- **Actualizar dependencias:** `pip install --upgrade -r requirements.txt`
- **Limpiar caché de Python:** `find . -type d -name __pycache__ -exec rm -rf {} +`
- **Git ignore:** El archivo `.gitignore` ya excluye `.venv/` y `__pycache__/`

---

## 📚 Recursos y referencias

- [Documentación de aiohttp](https://docs.aiohttp.org/)
- [BeautifulSoup4 docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Playwright Python](https://playwright.dev/python/)
- [Multiprocessing en Python](https://docs.python.org/3/library/multiprocessing.html)
- [Pytest documentation](https://docs.pytest.org/)

---

## 👥 Autor

**Valentin Barzola**  
Universidad de Mendoza – Computación II  
Año: 2025

---

## 📄 Licencia

Este proyecto es de uso académico y educativo.

---

