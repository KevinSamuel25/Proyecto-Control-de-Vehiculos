# Participantes:

Daniel Rojas Portillo C5J232
Malcolm Méndez C4H192
Yariel Jiménez C4G183

# Proyecto-Control-de-Vehiculos

API REST con Django y Django REST Framework para la gestión de una flota
vehicular y su taller: vehículos, mantenimientos preventivos, órdenes de
trabajo, inventario de repuestos y proveedores.

## Requisitos

- Python 3.12+
- MySQL 8.0+ (o MariaDB compatible) — para pruebas rápidas se puede usar
  SQLite con `DB_ENGINE=sqlite` (ver más abajo).
- Dependencias en `requirements.txt` (Django, DRF, mysqlclient, pillow).

## Instalación

```bash
# 1. Clonar el repositorio y entrar a la carpeta.

# 2. Crear y activar el entorno virtual.
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependencias.
pip install -r requirements.txt

# 4. Configurar variables de entorno.
cp .env.example .env   # Windows: copy .env.example .env
# Editar .env con la SECRET_KEY y las credenciales de MySQL.
```

## Base de datos (MySQL)

Crear la base de datos y el usuario (una sola vez):

```sql
CREATE DATABASE control_vehiculos_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

Configure `DB_USER` y `DB_PASSWORD` en `.env` con un usuario de MySQL que tenga
permisos sobre esta base de datos. Para desarrollo local puede utilizarse `root`,
pero no se recomienda usarlo en producción.
```

## Migraciones y usuarios de prueba

```bash
python manage.py migrate
python manage.py crear_usuarios_demo   # roles + usuarios de prueba
python manage.py createsuperuser       # opcional, para el admin de Django
python manage.py runserver
```

El comando `crear_usuarios_demo` crea los grupos de roles y estos usuarios:

| Usuario     | Contraseña      | Rol                  |
|-------------|-----------------|----------------------|
| `admin`     | `Admin123*`     | Administrador (staff)|
| `operador`  | `Operador123*`  | Operador             |
| `consulta`  | `Consulta123*`  | Consulta             |

## Ejecución de pruebas automatizadas

Las pruebas no requieren servidor MySQL (usan SQLite en memoria):

```bash
python manage.py test
```

Son 34 pruebas: 5 casos CRUD, reglas de negocio (respuestas 400),
3 permisos (401/403) y casos de paginación y filtros.

## Autenticación

Autenticación por token de DRF. Obtener el token:

```
POST /api/auth/login/
{ "username": "operador", "password": "Operador123*" }
```

Usar el token en cada solicitud:

```
Authorization: Token <token>
```

## Matriz de permisos

| Recurso / operación              | Administrador | Operador | Consulta |
|----------------------------------|:-------------:|:--------:|:--------:|
| Vehículos (CRUD)                 | CRUD          | Lectura  | Lectura  |
| Mantenimientos (CRUD)            | CRUD          | Lectura  | Lectura  |
| Proveedores (CRUD)               | CRUD          | Lectura  | Lectura  |
| Repuestos (CRUD)                 | CRUD          | Lectura  | Lectura  |
| Órdenes de trabajo (crear/editar)| Sí            | Sí       | No (403) |
| Órdenes de trabajo (eliminar)    | Sí            | No (403) | No (403) |
| Comentarios/consumos (crear)     | Sí            | Sí       | No (403) |
| Consumo de repuesto (`/consumos/`)| Sí           | Sí       | No (403) |
| Resumen de inventario (lectura)  | Sí            | Sí       | Sí       |

Convención HTTP: usuario anónimo → **401**; rol sin permiso → **403**.

## Reglas de negocio

| ID    | Regla | Respuesta |
|-------|-------|-----------|
| RN-01 | La placa es única y se normaliza a mayúsculas/sin espacios. | 400 |
| RN-02 | El kilometraje objetivo de un mantenimiento debe ser mayor al kilometraje actual del vehículo (también en PATCH). | 400 |
| RN-03 | Un vehículo solo puede tener una orden de trabajo activa (ABIERTA o EN_PROCESO). | 400 |
| RN-04 | Una orden COMPLETADA o CANCELADA es inmutable (también en PATCH). | 400 |
| RN-05 | Completar una orden exige registrar la fecha de salida. | 400 |
| RN-06 | La fecha de salida no puede ser anterior a la fecha de ingreso. | 400 |
| RN-07 | El costo total de una orden nunca puede ser negativo. | 400 |
| RN-08 | Solo se pueden agregar repuestos a órdenes activas (ABIERTA o EN_PROCESO). | 400 |
| RN-09 | No se puede consumir más cantidad de la disponible en inventario (stock). | 400 |

Además, los borrados protegidos por integridad referencial (proveedor o
repuesto con registros asociados) devuelven **409 CONFLICT**.

## Catálogo de endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Devuelve el token y los roles del usuario. |
| POST | `/api/auth/logout/` | Invalida el token del usuario autenticado. |
| GET  | `/api/auth/perfil/` | Datos del usuario autenticado y sus roles. |

### Vehículos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/vehiculos/` | Lista paginada. Filtros: `estado`, `kilometraje_min`, `kilometraje_max`, `page`. |
| POST | `/api/vehiculos/` | Crea un vehículo (admin). |
| GET | `/api/vehiculos/<id>/` | Consulta un vehículo. |
| PUT/PATCH | `/api/vehiculos/<id>/` | Actualiza un vehículo (admin). |
| DELETE | `/api/vehiculos/<id>/` | Elimina un vehículo (admin). |

### Mantenimientos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mantenimientos/` | Lista paginada. Filtros: `estado`, `vehiculo`, `page`. |
| POST | `/api/mantenimientos/` | Programa un mantenimiento (admin). |
| GET | `/api/mantenimientos/<id>/` | Consulta un mantenimiento. |
| PUT/PATCH | `/api/mantenimientos/<id>/` | Actualiza un mantenimiento (admin). |
| DELETE | `/api/mantenimientos/<id>/` | Elimina un mantenimiento (admin). |

### Órdenes de trabajo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/ordenes/` | Lista paginada. Filtros: `estado`, `vehiculo`, `buscar` (código o falla), `page`. |
| POST | `/api/ordenes/` | Crea una orden (operador o admin). |
| GET | `/api/ordenes/<id>/` | Consulta una orden. |
| PUT/PATCH | `/api/ordenes/<id>/` | Actualiza una orden (operador o admin). |
| DELETE | `/api/ordenes/<id>/` | Elimina una orden (solo admin). |

### Comentarios / consumos de órdenes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/comentarios/` | Lista paginada. Filtro: `orden`, `page`. |
| POST | `/api/comentarios/` | Agrega un repuesto consumido a una orden (operador o admin). |
| GET | `/api/comentarios/<id>/` | Consulta un consumo. |
| DELETE | `/api/comentarios/<id>/` | Elimina un consumo (solo admin). |

### Inventario de repuestos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/inventario/` | Lista paginada. Filtros combinables: `buscar`, `proveedor`, `bajo_stock` (0/1); ordenamiento: `ordenar` (`id`, `nombre`, `precio_unitario`, `-precio_unitario`, `stock`, `-stock`); `page`. |
| POST | `/api/inventario/` | Crea un repuesto (admin). |
| GET | `/api/inventario/resumen/` | Agregación: total de tipos, unidades y valor del inventario. |
| POST | `/api/inventario/consumos/` | Registra el consumo de un repuesto en una orden: descuenta stock y suma al costo de la orden (operador o admin). Cuerpo: `{ "orden", "repuesto", "cantidad" }`. |
| GET | `/api/inventario/<id>/` | Consulta un repuesto. |
| PUT/PATCH | `/api/inventario/<id>/` | Actualiza un repuesto (admin). |
| DELETE | `/api/inventario/<id>/` | Elimina un repuesto (admin); 409 si tiene consumos asociados. |

### Proveedores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/proveedores/` | Lista paginada. Búsqueda: `buscar` (nombre o cédula), `page`. |
| POST | `/api/proveedores/` | Crea un proveedor (admin). |
| GET | `/api/proveedores/<id>/` | Consulta un proveedor. |
| PUT/PATCH | `/api/proveedores/<id>/` | Actualiza un proveedor (admin). |
| DELETE | `/api/proveedores/<id>/` | Elimina un proveedor (admin); 409 si tiene repuestos asociados. |

Las respuestas de listado incluyen `pagina_actual`, `total_paginas`,
`total_registros` y `resultados`.

## Colección Postman

En `postman/vehiculos-mantenimientos.postman_collection.json` hay 24 solicitudes
organizadas por modulo. Configurar la variable de colección `baseUrl` con
`http://127.0.0.1:8000/api` y `token` con el valor devuelto por `/api/auth/login/`.

## Flujo de negocio

1. El administrador carga los catálogos: proveedores, repuestos, vehículos
   y mantenimientos programados.
2. El operador registra la orden de trabajo de un vehículo que ingresa al
   taller (un vehículo solo puede tener una orden activa).
3. Durante el servicio, el operador consume repuestos: el sistema descuenta
   el inventario de forma atómica (`select_for_update` + `F()`) y acumula
   el costo en la orden.
4. Al completar la orden se exige la fecha de salida; la queda cerrada e
   inmutable y libera al vehículo para una nueva orden.

## Limitaciones conocidas

- Sin endpoints de carga masiva ni reportes exportables.
- La paginación es por número de página (tamaño fijo: 5 u 10 según el
  recurso), no configurable por el cliente.
- El inventario no registra movimientos de entrada (compras) ni ajustes;
  solo salidas por consumo.
