# INFO.md — Decisiones de diseño del sistema
### Sistema Distribuido de Reservas de Canchas de Pádel
**Autor:** Valentín Barzola — Computación II, Universidad de Mendoza

---

## 1. Sockets TCP — Capa de transporte

### ¿Qué es un socket?
Un socket es el extremo de una conexión de red. Actúa como puente entre los clientes y el servidor, permitiendo la transmisión de datos a través de la red. En este proyecto, los clientes envían sus solicitudes de reserva en formato JSON a través de sockets.

### ¿Por qué TCP y no UDP?
Se eligió TCP (Transmission Control Protocol) porque garantiza:
- **Entrega ordenada**: los paquetes llegan en el orden en que fueron enviados.
- **Entrega garantizada**: si un paquete se pierde, TCP lo detecta y lo reenvía automáticamente.
- **Handshake de conexión**: antes de transmitir datos, cliente y servidor establecen una conexión explícita.

UDP no garantiza la entrega de paquetes. En un sistema de reservas, un mensaje perdido significaría una reserva fantasma o perdida, lo cual es inaceptable.

### Estructura de sockets en el servidor
El servidor no tiene un único socket. Tiene dos tipos:
- **Socket de escucha**: se abre una sola vez, se liga a un puerto (ej: 5000) y espera conexiones entrantes. Solo acepta — nunca transmite datos de aplicación.
- **Socket de conexión**: por cada cliente que se conecta, el servidor crea un socket nuevo dedicado a esa conversación. El socket de escucha queda libre para seguir esperando nuevos clientes.

Todo esto ocurre en un **único puerto**. El sistema operativo distingue cada conexión mediante el par `(IP origen + puerto efímero del cliente) + (IP servidor + puerto servidor)`, que es único para cada conexión.

### ¿Por qué no se necesitó esto en APIs con Flask/FastAPI?
Cuando se construye una API con frameworks como Flask o FastAPI, los sockets existen igual pero están ocultos dentro del framework. El framework abre el socket, escucha, acepta conexiones y parsea HTTP automáticamente. En este proyecto se trabaja directamente con la capa de transporte, sin la capa HTTP del medio, usando JSON crudo sobre TCP.

### Posibles preguntas de examen
- **¿Por qué TCP y no UDP?** → TCP garantiza entrega y orden, crítico para reservas donde un mensaje perdido es inaceptable.
- **¿Cuántos sockets tiene el servidor?** → Uno de escucha permanente más uno nuevo por cada cliente conectado.
- **¿En cuántos puertos escucha el servidor?** → Uno solo. El SO distingue conexiones por el par IP:puerto de cada extremo.

---

## 2. Asyncio — Recepción concurrente de clientes

### ¿Qué es asyncio?
`asyncio` es una librería estándar de Python (no requiere instalación). Más que una librería, es un **modelo de ejecución** que permite manejar múltiples operaciones de red de forma concurrente en un solo hilo, sin bloquearse.

### El problema que resuelve
Sin asyncio, cuando el servidor hace `recv()` para leer datos de un cliente, Python se queda parado esperando hasta que lleguen los datos. Con 50 clientes conectados, el servidor atiende uno y deja a los otros 49 esperando.

### ¿Cómo lo resuelve asyncio?
Con un mecanismo de **cesión de control**. Cuando una operación de red va a tardar, en lugar de bloquearse, la corrutina cede el control al event loop para que atienda a otra. Esto se logra con dos palabras clave:

- **`async def`**: define una corrutina, una función que puede pausarse y retomarse.
- **`await`**: el punto exacto donde se cede el control. No significa "esperar bloqueado" sino "cedé el control mientras esperás, atendé a otro".

### El Event Loop
Es el motor central de asyncio. Corre en un ciclo infinito mientras el servidor está activo:
1. Revisa qué corrutinas están listas para continuar.
2. Ejecuta una hasta que hace `await`.
3. La pausa y vuelve al paso 1.

Se arranca con `asyncio.run(main())` y desde ahí maneja todo automáticamente.

### El handler
`handle_client()` es la corrutina que se ejecuta una vez por cada cliente nuevo. asyncio la llama automáticamente al detectar una conexión. Dentro del handler el servidor:
1. Recibe el JSON con `await reader.read()`
2. Valida el formato del JSON (campos requeridos, tipos de datos, formato de fecha)
3. Valida disponibilidad básica
4. Asigna un ID de turno único (usando `uuid`)
5. Encola la tarea en la cola IPC
6. Responde al cliente con `{"status": "recibido", "turno_id": "..."}` usando `await writer.drain()`

### ¿Por qué asyncio y no un hilo por cliente?
Crear un hilo por cliente tiene un costo alto en memoria y cambios de contexto del sistema operativo. Con muchos clientes concurrentes ese overhead se vuelve un problema. Las operaciones de red son I/O-bound — el tiempo se pasa esperando datos, no calculando. asyncio maneja decenas de clientes con un solo hilo porque mientras uno espera datos, el event loop atiende a otro.

### Posibles preguntas de examen
- **¿Qué es el event loop?** → El motor central de asyncio que corre en ciclo infinito, ejecuta corrutinas hasta que hacen `await` y cede el control a otra.
- **¿Qué hace `await`?** → Cede el control al event loop para que atienda otra corrutina mientras la actual espera una operación de red.
- **¿Por qué asyncio y no threads?** → Las operaciones de red son I/O-bound. asyncio maneja muchas conexiones con un solo hilo sin el overhead de crear y cambiar entre threads.
- **¿Quién llama al handler?** → asyncio lo llama automáticamente por cada cliente nuevo que se conecta.
- **¿Por qué el servidor asigna el ID y no el worker?** → Porque necesita responderle algo concreto al cliente de inmediato. Si el ID lo asignara el worker, el cliente debería quedarse conectado hasta que el worker termine, arruinando la ventaja del diseño asíncrono.

---

## 3. Cola IPC — Comunicación entre procesos

### ¿Qué es IPC?
IPC significa *Inter-Process Communication* — comunicación entre procesos. El servidor (asyncio) y los workers (multiprocessing) son procesos completamente separados en el sistema operativo, con memoria separada. No pueden compartir una variable directamente. La `multiprocessing.Queue` es el canal seguro que el SO les provee para pasarse datos.

### ¿Cómo funciona?
La cola funciona como un buzón FIFO (First In, First Out): la primera tarea que entra es la primera que sale. El servidor mete tareas con `queue.put()` y los workers las sacan con `queue.get()`.

```
Servidor → queue.put(tarea) → [tarea1, tarea2, tarea3] → queue.get() → Worker
```

### ¿Qué viaja en la cola?
Cada elemento de la cola es un diccionario Python (que viene del JSON del cliente) con todos los datos del turno: ID, cancha, horario, nombre del jugador, etc.

### Diferencia con asyncio
- `asyncio` resuelve **concurrencia** dentro de un proceso (muchos clientes, un hilo).
- `multiprocessing.Queue` resuelve **comunicación** entre procesos distintos.
Son dos problemas distintos y el sistema usa ambos.

### Posibles preguntas de examen
- **¿Por qué se llama IPC?** → Porque comunica procesos distintos que no comparten memoria.
- **¿Por qué no una variable global compartida?** → El servidor y los workers son procesos separados del SO — no comparten espacio de memoria. Una variable global solo existe dentro de un proceso.
- **¿Qué orden tienen las tareas?** → FIFO. La primera reserva que llega es la primera que se procesa.

---

## 4. Workers — Procesamiento paralelo

### ¿Qué son los workers?
Son procesos independientes del sistema operativo que corren en paralelo. Cada worker ejecuta un ciclo infinito: toma una tarea de la cola, la procesa y guarda el resultado. La cantidad de workers se configura por línea de comandos (`--workers N`).

### ¿Qué hace cada worker?
1. **`queue.get()`** — espera bloqueado hasta que haya una tarea disponible. Este bloqueo solo afecta al worker, nunca al servidor.
2. **Validación de negocio** — valida reglas de dominio: ¿la cancha existe? ¿el horario está dentro del rango permitido? ¿hay conflicto con otra reserva ya registrada?
3. **Procesamiento** — calcula precio, confirma el turno, genera el comprobante.
4. **Persistencia** — guarda la reserva en el archivo de registro (JSON o base de datos).

### ¿Por qué multiprocessing y no threads?
Python tiene el **GIL** (Global Interpreter Lock): un mecanismo del intérprete que impide que dos threads ejecuten código Python al mismo tiempo dentro del mismo proceso.

- **Threads + I/O**: el GIL no es problema. Mientras un thread espera datos de red, libera el GIL y otro puede correr. Por eso asyncio funciona bien.
- **Threads + CPU**: el GIL sí es problema. Aunque haya 4 threads queriendo calcular al mismo tiempo, solo uno puede ejecutar código Python a la vez. No hay paralelismo real.

Los workers hacen trabajo CPU (validaciones, cálculos, escritura a disco). Con `multiprocessing`, cada worker es un proceso real del SO con su propio intérprete y su propio GIL. Corren en paralelo en distintos núcleos del procesador — paralelismo verdadero.

### Posibles preguntas de examen
- **¿Qué es el GIL?** → El Global Interpreter Lock de Python. Impide que dos threads ejecuten código Python simultáneamente en el mismo proceso.
- **¿Por qué multiprocessing y no threads para los workers?** → Los workers hacen trabajo CPU. El GIL impediría el paralelismo real con threads. Con multiprocessing cada proceso tiene su propio GIL y corren en paralelo en distintos núcleos.
- **¿Por qué threads sí funcionan para asyncio pero no para los workers?** → asyncio es I/O-bound: el tiempo se pasa esperando datos de red, no calculando. El GIL se libera durante I/O. Los workers son CPU-bound: necesitan calcular, y ahí el GIL bloquea.
- **¿Cuántos workers se usan?** → Se configura con `--workers N` por línea de comandos. Es una decisión de diseño consciente para poder ajustarlo según la carga del sistema.

---

## Resumen de decisiones de diseño

| Componente | Tecnología | Justificación |
|---|---|---|
| Capa de transporte | Sockets TCP | Entrega garantizada y ordenada, crítico para reservas |
| Recepción concurrente | asyncio | I/O-bound, un hilo alcanza, sin overhead de threads |
| Comunicación entre procesos | multiprocessing.Queue | Procesos separados no comparten memoria, cola FIFO segura |
| Procesamiento de reservas | multiprocessing workers | CPU-bound, necesita paralelismo real, evita el GIL |
| Formato de datos | JSON | Legible, estándar, fácil de validar y serializar |
| Identificación de turnos | uuid4 | Garantiza unicidad sin necesidad de coordinación entre procesos |
| Configuración | argparse | Permite ajustar host, puerto y workers sin modificar el código |