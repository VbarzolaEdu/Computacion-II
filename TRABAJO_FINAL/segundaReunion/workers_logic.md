# Lógica de negocio — Workers

## Validaciones obligatorias

**Disponibilidad de cancha**
Verificar que la cancha solicitada no tenga otra reserva en el mismo horario.
Es la validación más crítica del sistema. Requiere un `Lock` de sincronización
porque dos workers podrían verificar disponibilidad simultáneamente, ver la cancha
libre ambos, y confirmar dos reservas para el mismo horario — race condition clásica.

```python
with lock:
    if cancha_disponible(cancha, horario):
        guardar_reserva(tarea)
    else:
        rechazar_reserva(tarea)
```

**Rango horario válido**
Verificar que el horario solicitado esté dentro del horario de apertura del club.
Ejemplo: no aceptar reservas fuera del rango 08:00–23:00.

**Existencia de cancha**
Verificar que el número de cancha exista en el sistema.
Ejemplo: si el club tiene 6 canchas, rechazar cualquier solicitud para cancha 7 o superior.

---

## Cálculo de precio

Trabajo CPU real que justifica el uso de workers independientes.

| Criterio | Detalle |
|---|---|
| Horario pico | 18:00–22:00 tiene precio mayor |
| Horario valle | Antes de las 12:00 tiene descuento |
| Tipo de cancha | Techada más cara que al aire libre |
| Duración | Precio proporcional a 60 o 90 minutos |

---

## Descuentos y ofertas

| Descuento | Condición |
|---|---|
| Socio del club | El jugador figura como socio en la BD |
| Reserva anticipada | Reserva con más de 48hs de anticipación |
| Horario valle | Automático por franja horaria de baja demanda |

---

## Límite de reservas por jugador

Verificar que el jugador no supere el máximo de reservas permitidas por semana.
Ejemplo: máximo 3 reservas por jugador por semana para garantizar disponibilidad.

---

## Race condition en disponibilidad — punto clave del examen

El caso crítico es cuando dos clientes solicitan la misma cancha en el mismo horario
de forma simultánea. Sin sincronización el flujo sería:

```
Worker 1 consulta BD → cancha libre
Worker 2 consulta BD → cancha libre        ← ambos ven libre al mismo tiempo
Worker 1 confirma reserva → guarda en BD
Worker 2 confirma reserva → guarda en BD   ← doble reserva, race condition
```

Con `multiprocessing.Lock` el flujo correcto es:

```
Worker 1 adquiere lock → consulta → confirma → guarda → libera lock
Worker 2 espera lock   → consulta → cancha ocupada → rechaza → libera lock
```

Solo un worker a la vez puede ejecutar el bloque de verificación y escritura,
eliminando la posibilidad de doble reserva.