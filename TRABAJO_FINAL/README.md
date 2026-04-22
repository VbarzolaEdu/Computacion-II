# Sistema de Reservas de Pádel

Sistema de servidor TCP con arquitectura asyncio + ProcessPoolExecutor para procesar reservas de canchas de pádel.

## Arquitectura

```
Clientes TCP
    ↓
Servidor Asyncio (event loop)
    ↓ await run_in_executor()
ProcessPoolExecutor (pool de workers)
    ↓
Base de Datos
```

### Componentes

- **server/**: Servidor asyncio, handlers de clientes, dispatcher
- **workers/**: Pool de workers, tareas de procesamiento, validaciones
- **models/**: Esquemas y modelos de dominio
- **database/**: Conexión y queries a BD
- **utils/**: Configuración, logging, excepciones

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

Configurable por variables de entorno:

```bash
SERVER_HOST=0.0.0.0 SERVER_PORT=5000 NUM_WORKERS=4 python main.py
```

## Testing

```bash
pytest tests/
```

## Protocolo

Los clientes envían JSON por TCP en una línea:

```json
{
  "cliente_id": "cliente_001",
  "cancha_id": "cancha_1",
  "horario": "10:00-11:00",
  "precio": 50.0,
  "fecha": "2026-04-20"
}
```

El servidor responde con:

```json
{
  "status": "success",
  "id": "1234567890-5678",
  "data": {
    "reserva_id": "1",
    "estado": "confirmada",
    "mensaje": "Reserva guardada exitosamente"
  }
}
```
