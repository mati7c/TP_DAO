# Cliente
from .cliente_controller import listar_clientes, crear_cliente, borrar_cliente
# Empleado
from .empleado_controller import listar_empleados, crear_empleado, borrar_empleado
# Vehículo
from .vehiculo_controller import listar_vehiculos, crear_vehiculo, borrar_vehiculo, buscar_vehiculos_disponibles
# Alquiler
from .alquiler_controller import listar_alquileres, crear_alquiler, iniciar_alquiler, finalizar_alquiler
# Mantenimiento
from .mantenimiento_controller import listar_mantenimientos, finalizar_mantenimiento, programar_mantenimiento
# Incidente
from .incidente_controller import cargar_dano, cargar_multa
# Reporte
from .reporte_controller import reporte_historial_cliente, reporte_ranking_vehiculos, reporte_alquileres_periodo, reporte_facturacion_mensual