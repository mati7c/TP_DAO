from django.urls import path
from gestion.controllers import (
    listar_clientes, crear_cliente, borrar_cliente,
    listar_empleados, crear_empleado, borrar_empleado,
    listar_vehiculos, crear_vehiculo, borrar_vehiculo
)

urlpatterns = [
    # Clientes
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/crear/', crear_cliente, name='crear_cliente'),
    path('clientes/borrar/<int:dni>/', borrar_cliente, name='borrar_cliente'),

    # Empleados
    path('empleados/', listar_empleados, name='listar_empleados'),
    path('empleados/crear/', crear_empleado, name='crear_empleado'),
    path('empleados/borrar/<int:dni>/', borrar_empleado, name='borrar_empleado'),

    # Vehículos
    path('vehiculos/', listar_vehiculos, name='listar_vehiculos'),
    path('vehiculos/crear/', crear_vehiculo, name='crear_vehiculo'),
    path('vehiculos/borrar/<str:patente>/', borrar_vehiculo, name='borrar_vehiculo'),
]