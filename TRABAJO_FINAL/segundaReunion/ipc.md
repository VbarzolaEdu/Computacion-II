# Reunión 01 — Decisión de arquitectura: Pool de workers

## Problema identificado

En el diseño inicial, el sistema contaba con dos procesos principales: el servidor asyncio
para recepción de clientes y workers independientes consumiendo una cola FIFO manual
mediante `multiprocessing.Queue`. Se identificó que este esquema desperdiciaba paralelismo:
un worker ocupado con una tarea pesada dejaba a los siguientes turnos esperando en la cola
aunque hubiera otros workers libres disponibles.

## Solución adoptada: ProcessPoolExecutor

Se decidió reemplazar la cola FIFO manual por un **pool de workers** usando `ProcessPoolExecutor`.
El pool mantiene un conjunto de procesos activos y un dispatcher interno que asigna cada tarea
al primer worker libre, sin depender del orden de llegada.

La integración con asyncio se realiza mediante `loop.run_in_executor()`, que permite delegar
el procesamiento al pool **sin bloquear el event loop** — el servidor sigue recibiendo reservas
de otros jugadores mientras el pool procesa en paralelo.

## Por qué se mantienen dos procesos separados

Se evaluó la alternativa de procesar todo dentro del servidor asyncio, pero se descartó por
las siguientes razones:

- **El event loop no debe ejecutar trabajo CPU.** La lógica de negocio (validar disponibilidad
  de cancha, calcular precio, guardar la reserva) es CPU-bound. Ejecutarla dentro del event loop
  lo bloquearía durante cada procesamiento, impidiendo recibir nuevas conexiones de clientes.
- **Responsabilidades distintas requieren tecnologías distintas.** Recibir conexiones es I/O-bound
  → asyncio es la herramienta correcta. Procesar reservas es CPU-bound → multiprocessing es
  la herramienta correcta. Unificarlos obligaría a usar una sola tecnología para dos problemas
  con naturalezas opuestas.
- **Modularidad.** Cada componente tiene una responsabilidad única. Cambios en la lógica de
  negocio (precios, reglas de reserva) no afectan al servidor de red y viceversa.
- **Escalabilidad independiente.** Si el cuello de botella es el procesamiento, se agregan
  workers. Si es la recepción de conexiones, se ajusta el servidor. Con un solo proceso,
  no es posible escalar una parte sin afectar la otra.

## Flujo resultante

```
Cliente → [TCP/JSON] → Servidor asyncio → run_in_executor() → ProcessPoolExecutor
                ↑                                                      ↓
         "turno recibido"                                    Worker libre procesa
                                                             valida + calcula + guarda
```