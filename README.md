# Proyecto-Control-de-Vehiculos
Proyecto Desarrollo problema de negocio

## API de flota y mantenimientos

La API bajo `/api/`:

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/vehiculos/` | Lista paginada; acepta `page`, `estado`, `kilometraje_min` y `kilometraje_max`. |
| POST | `/api/vehiculos/` | Crea un vehículo. Requiere usuario administrador. |
| GET | `/api/vehiculos/<id>/` | Consulta un vehículo. |
| PUT/PATCH | `/api/vehiculos/<id>/` | Actualiza un vehículo. Requiere usuario administrador. |
| DELETE | `/api/vehiculos/<id>/` | Elimina un vehículo. Requiere usuario administrador. |
| GET | `/api/mantenimientos/` | Lista paginada con `page`, `estado` y `vehiculo`. |
| POST | `/api/mantenimientos/` | Programa un mantenimiento. Requiere usuario administrador. |
| GET | `/api/mantenimientos/<id>/` | Consulta un mantenimiento. |
| PUT/PATCH | `/api/mantenimientos/<id>/` | Actualiza un mantenimiento. Requiere usuario administrador. |
| DELETE | `/api/mantenimientos/<id>/` | Elimina un mantenimiento. Requiere usuario administrador. |

Las respuestas de listado incluyen `pagina_actual`, `total_paginas`,
`total_registros` y `resultados`. Las placas se normalizan a mayúsculas y
deben ser únicas; el kilometraje objetivo de un mantenimiento debe ser mayor
que el kilometraje actual del vehículo.
