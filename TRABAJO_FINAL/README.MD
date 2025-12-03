# 🏟️ Sistema Distribuido de Reservas de Canchas de Pádel  
### **Trabajo Final – Computación II**  
### **Autor: Valentín Barzola**

Este proyecto implementa un sistema distribuido para la gestión de reservas de canchas de pádel en Mendoza.  
El sistema utiliza **sockets TCP**, **asincronismo con asyncio**, y **procesos en paralelo mediante multiprocessing** para manejar múltiples clientes simultáneos y procesar las reservas de manera eficiente. Cada solicitud es enviada por un cliente en formato JSON, atendida por un servidor no bloqueante y finalmente procesada por workers independientes que operan a través de una cola de tareas distribuida.


## Arquitectura

                             ┌───────────────────────────────────────────┐
                             │                 CLIENTES                  │
                             │───────────────────────────────────────────│
                             │ Envían solicitud de reserva vía TCP/JSON  │
                             │ (nombre, club, fecha, hora, cancha, etc)  │
                             └───────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                   ┌───────────────────────────────────────────────────────────┐
                   │                     SERVIDOR PRINCIPAL                    │
                   │                         (asyncio)                         │
                   │───────────────────────────────────────────────────────────│
                   │ - Escucha conexiones TCP                                  │
                   │ - Maneja múltiples clientes concurrentes (asyncio)        │
                   │ - Por cada cliente:                                       │
                   │       • Recibe JSON con datos del turno                   │
                   │       • Valida formato y disponibilidad básica            │
                   │       • Asigna ID de turno                                │
                   │       • Encola la tarea para procesamiento                │
                   │ - Responde al cliente: "turno_recibido"                   │
                   └──────────────────────┬────────────────────────────────────┘
                                          │   IPC (multiprocessing.Queue)
                                          ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                                   COLA IPC                                  │ 
        │                         (multiprocessing.Queue)                             │
        │─────────────────────────────────────────────────────────────────────────────│
        │  Actúa como buffer de tareas entre                                          │
        │  el servidor principal y los workers.                                       │
        │  Cada elemento en la cola es un JSON con todos los datos del turno.         │
        └──────────────────────────┬──────────────────────────────────────────────────┘
                                   │
                                   ▼
          ┌──────────────────────────────────────────────────────────────────────┐
          │                                WORKERS                               │
          │                           (multiprocessing)                          │
          │──────────────────────────────────────────────────────────────────────│
          │ - Cada worker es un proceso independiente                            │
          │ - Consumen tareas de la cola IPC                                     │
          │ - Procesan la reserva:                                               │
          │     • Simulan lógica de negocio (precio, validación horaria, etc.)   │
          │     • Registran el turno (archivo/log/registro interno)              │
          │ - Funcionan en paralelo para acelerar el procesamiento                │
          └───────────────────────────┬──────────────────────────────────────────┘
                                      │
                                      ▼
                 ┌─────────────────────────────────────────────────────────┐
                 │                        REGISTRO                         │
                 │           (archivo JSON, log o base simple)             │
                 │──────────────────────────────────────────────────────── │
                 │ Los workers guardan los turnos procesados para          │
                 │ consulta posterior, auditoría o debug.                  │
                 └─────────────────────────────────────────────────────────┘


## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Servidor

```bash
python server.py --host 0.0.0.0 --port 5000 --workers 4
```

**Parámetros:**
- `--host`: IP del servidor (default: `localhost`)
- `--port`: Puerto (default: `5000`)
- `--workers`: Número de workers (default: `4`)

### Cliente

```bash
python client.py --host localhost --port 5000 --cancha 1 --horario "2025-12-10 18:00"
```

**Parámetros:**
- `--host`: IP del servidor
- `--port`: Puerto del servidor
- `--cancha`: Número de cancha (1-10)
- `--horario`: Fecha y hora (formato: `YYYY-MM-DD HH:MM`)

## Ejemplo de uso completo

Terminal 1 (Servidor):
```bash
python server.py --host localhost --port 5000 --workers 2
```

Terminal 2 (Cliente):
```bash
python client.py --host localhost --port 5000 --cancha 3 --horario "2025-12-15 19:00"
```

## Tests

```bash
pytest tests/
```

## Estructura del proyecto

```
.
├── server.py           # Servidor asyncio con sockets TCP
├── client.py           # Cliente CLI
├── workers.py          # Workers con multiprocessing
├── requirements.txt    # Dependencias
├── tests/              # Tests con pytest
└── README.MD           # Este archivo
```

---
**Autor:** Valentin Barzola  
**Materia:** Computación II – Universidad de Mendoza