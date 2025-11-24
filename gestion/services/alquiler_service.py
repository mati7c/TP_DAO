from datetime import datetime

from gestion.models import Alquiler
from gestion.repositories.alquiler_repository import AlquilerRepository
from gestion.models.cliente import Cliente
from gestion.models.empleado import Empleado
from gestion.models.vehiculo import Vehiculo
from gestion.models.estado import Estado


class AlquilerService:
    def __init__(self):
        self.repo = AlquilerRepository()

    def listar_alquileres(self):
        return self.repo.get_all()

    def registrar_alquiler(self, dni_cliente, dni_empleado, patente, fecha_inicio_str, fecha_fin_str):
        # --- 1. Conversión de Fechas ---
        try:
            f_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")

        # --- 2. Validaciones de Negocio ---
        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fecha de fin.")

        # Calcular días (delta)
        delta = f_fin - f_inicio
        dias_calculados = delta.days

        # Si alquila y devuelve el mismo día, cobramos 1 día mínimo
        if dias_calculados == 0:
            dias_calculados = 1

        # --- 3. Obtener Instancias (Validar existencia) ---
        try:
            cliente = Cliente.objects.get(pk=dni_cliente)
        except Cliente.DoesNotExist:
            raise ValueError(f"Cliente {dni_cliente} no existe.")

        try:
            empleado = Empleado.objects.get(pk=dni_empleado)
        except Empleado.DoesNotExist:
            raise ValueError(f"Empleado {dni_empleado} no existe.")

        try:
            vehiculo = Vehiculo.objects.get(pk=patente)
        except Vehiculo.DoesNotExist:
            raise ValueError(f"Vehículo {patente} no existe.")

        # Validar Disponibilidad
        # Caso A: Mantenimiento (Nunca se puede alquilar si está roto)
        if vehiculo.id_estado.id == 3:
            raise ValueError("El vehículo está en mantenimiento.")

        # Caso B: Chequeo de fechas (Lo que acabamos de programar)
        # Verificamos si hay colisión en la tabla Alquiler para ese auto específico
        from django.db.models import Q
        colisiones = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],  # Confirmada o Activa
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colisiones:
            raise ValueError(f"El vehículo {patente} ya tiene una reserva en esas fechas.")

        # --- 4. Obtener Estado 'Activo' (ID 7) ---
        try:
            estado_activo = Estado.objects.get(pk=7)
        except Estado.DoesNotExist:
            raise ValueError("El estado 'Activo' (ID 7) no está cargado en la base de datos.")

        # --- 5. Cálculos Monetarios ---
        # precio_x_dia es Decimal, dias es int. Python maneja esto bien.
        monto_calculado = vehiculo.precio_x_dia * dias_calculados

        # --- 6. Persistencia ---
        datos = {
            'fecha_inicio': f_inicio,
            'fecha_fin': f_fin,
            'dias_alquiler': dias_calculados,
            'monto_alquiler': monto_calculado,
            'monto_total': monto_calculado,  # Al inicio es igual
            'dni_cliente': cliente,
            'dni_empleado': empleado,
            'patente_vehiculo': vehiculo,
            'id_estado': estado_activo
        }

        nuevo_alquiler = self.repo.create(datos)

        # --- 7. Actualizar Estado del Vehículo ---
        # Pasamos el vehículo a "Alquilado" (ID 2)
        try:
            estado_alquilado = Estado.objects.get(pk=2)
            vehiculo.id_estado = estado_alquilado
            vehiculo.save()
        except:
            # Si falla esto, no es crítico para detener el alquiler, pero idealmente usamos transacciones
            pass

        return nuevo_alquiler

