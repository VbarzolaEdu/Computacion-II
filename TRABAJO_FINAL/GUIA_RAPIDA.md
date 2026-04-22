# Guía Rápida - Sistema de Reservas

## Setup Inicial

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Inicializar BD
python3 init_db.py

# 3. Iniciar servidor
python3 main.py
```

## Prueba rápida

En otra terminal:

```bash
# Cliente TCP simple
python3 client_example.py --host 127.0.0.1 --port 5000

# O múltiples requests simultáneos
python3 client_example.py --multiple 3
```

## Flujo de una Reserva

```
1. Cliente envía JSON por TCP
   {"cliente_id": "...", "cancha_id": "...", ...}

2. Servidor asyncio (handle_client) recibe y valida JSON

3. Dispatcher delega a worker via run_in_executor()

4. Worker (proceso separado) ejecuta procesar_reserva()
   - Valida negocio (validar_reserva)
   - Guarda en BD
   - Retorna resultado

5. Evento en asyncio se dispara (task completed)

6. Servidor envía respuesta al cliente
   {"status": "success", "id": "...", "data": {...}}
```

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Entry point del servidor |
| `server/servidor.py` | AsyncioServer, event loop, TCP |
| `server/dispatcher.py` | Delega a workers (run_in_executor) |
| `workers/tasks.py` | procesar_reserva() (se ejecuta en workers) |
| `workers/validation.py` | Validaciones de negocio |
| `database/queries.py` | Guardar/obtener datos |
| `utils/config.py` | Configuración global (env vars) |
| `utils/logger.py` | Logging centralizado |

## Variables de Entorno

```bash
# Puerto del servidor (default: 5000)
export SERVER_PORT=5000

# Número de workers (default: 4)
export NUM_WORKERS=4

# Ubicación de BD (default: ./data/reservas.db)
export DB_PATH=./data/reservas.db

# Nivel de logging (default: INFO)
export LOG_LEVEL=DEBUG
```

## Conceptos Clave

### Asyncio (Concurrencia)
- Múltiples clientes conectados al mismo tiempo
- Non-blocking: el event loop no espera I/O
- Usa `await handle_client()` para cada cliente

### ProcessPoolExecutor (Paralelismo)
- Workers en procesos separados
- Ejecutan tareas bloqueantes sin afectar asyncio
- `await loop.run_in_executor()` delega al pool

### Dispatcher
- Coordina entre asyncio y workers
- Recibe tarea, la envía al executor
- Espera resultado y lo retorna al handler

## Testing

```bash
# Tests unitarios
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

## Próximas Mejoras

- [ ] Implementar todas las validaciones en `workers/validation.py`
- [ ] Agregar IPC (multiprocessing.Queue) para comunicación bidireccional
- [ ] Rate limiting en dispatcher
- [ ] Metrics/prometheus para monitoreo
- [ ] Autenticación de clientes
- [ ] Cache de canchas en memoria
- [ ] Gestión de transacciones DB
