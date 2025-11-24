from django.urls import path
from gestion.controllers import (
    listar_clientes, crear_cliente, borrar_cliente,
    listar_empleados, crear_empleado, borrar_empleado,
    listar_vehiculos, crear_vehiculo, borrar_vehiculo, buscar_vehiculos_disponibles,
    listar_alquileres, crear_alquiler, iniciar_alquiler, finalizar_alquiler,
    listar_mantenimientos, finalizar_mantenimiento,programar_mantenimiento,
    cargar_multa, cargar_dano
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
    path('vehiculos/buscar/', buscar_vehiculos_disponibles, name='buscar_vehiculos'),

    # Alquileres
    path('alquileres/', listar_alquileres, name='listar_alquileres'),
    path('alquileres/crear/', crear_alquiler, name='crear_alquiler'),
    path('alquileres/finalizar/<int:id_alquiler>', finalizar_alquiler, name='finalizar_alquiler'),
    path('alquileres/iniciar/', iniciar_alquiler, name='iniciar_alquiler'),
    path('alquileres/cargar-multa/', cargar_multa, name='cargar_multa'),
    path('alquileres/carar-dano/', cargar_dano, name='cargar_dano'),

    # Mantenimientos
    path('mantenimientos/', listar_mantenimientos, name='listar_mantenimientos'),
    path('mantenimientos/programar/', programar_mantenimiento, name='programar_mantenimiento'),
    path('mantenimientos/finalizar/<int:id_mantenimiento>/', finalizar_mantenimiento, name='finalizar_mantenimiento'),
]