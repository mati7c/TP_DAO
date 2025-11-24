from datetime import datetime

from gestion.models import Alquiler, Mantenimiento
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

        delta = f_fin - f_inicio
        dias_calculados = delta.days

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

        # --- 4. VALIDACIÓN DE DISPONIBILIDAD ---

        # A) Estado actual crítico: Si HOY está roto, no alquilamos (regla de seguridad)
        if vehiculo.id_estado.id == 3:
            raise ValueError("El vehículo está actualmente en mantenimiento y no puede ser alquilado.")

        # B) Colisión con MANTENIMIENTOS programados (Lo que faltaba)
        colision_mantenimiento = Mantenimiento.objects.filter(
            patente=patente,
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colision_mantenimiento:
            raise ValueError(f"El vehículo {patente} tiene un mantenimiento programado en esas fechas.")

        # C) Colisión con OTROS ALQUILERES
        colisiones_alquiler = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],  # Confirmada o Activa
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colisiones_alquiler:
            raise ValueError(f"El vehículo {patente} ya tiene una reserva confirmada en esas fechas.")

        # --- 5. Obtener Estado 'Activo' (ID 7) ---
        try:
            estado_activo = Estado.objects.get(pk=7)
        except Estado.DoesNotExist:
            raise ValueError("El estado 'Activo' (ID 7) no está cargado en la base de datos.")

        # --- 6. Cálculos y Persistencia ---
        monto_calculado = vehiculo.precio_x_dia * dias_calculados

        datos = {
            'fecha_inicio': f_inicio,
            'fecha_fin': f_fin,
            'dias_alquiler': dias_calculados,
            'monto_alquiler': monto_calculado,
            'monto_total': monto_calculado,
            'dni_cliente': cliente,
            'dni_empleado': empleado,
            'patente_vehiculo': vehiculo,
            'id_estado': estado_activo
        }

        nuevo_alquiler = self.repo.create(datos)

        # --- 7. Actualizar Estado del Vehículo ---
        # Si el alquiler empieza HOY, cambiamos el estado ya mismo a 'Alquilado' (2)
        from datetime import date
        if f_inicio == date.today():
            try:
                estado_alquilado = Estado.objects.get(pk=2)
                vehiculo.id_estado = estado_alquilado
                vehiculo.save()
            except:
                pass

        return nuevo_alquiler

    def finalizar_alquiler(self, id_alquiler, fecha_devolucion_str, lista_multas, lista_danos):
        # ... (Este método queda igual a como lo definimos antes) ...
        # Lo incluyo resumido para mantener el contexto si lo necesitas
        alquiler = self.repo.get_by_id(id_alquiler)
        if not alquiler:
            raise ValueError("Alquiler no encontrado.")

        if alquiler.id_estado.nombre == 'Finalizado':
            raise ValueError("Este alquiler ya fue finalizado.")

        try:
            f_devolucion = datetime.strptime(fecha_devolucion_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Fecha inválida.")

        if f_devolucion < alquiler.fecha_inicio:
            raise ValueError("La devolución no puede ser anterior al inicio.")

        recargo_mora = 0
        if f_devolucion > alquiler.fecha_fin:
            dias_extra = (f_devolucion - alquiler.fecha_fin).days
            precio_dia = alquiler.patente_vehiculo.precio_x_dia
            recargo_mora = dias_extra * precio_dia * 2

        total_multas = 0
        for m in lista_multas:
            monto = float(m['monto'])
            self.multa_repo.create({
                'descripcion': m['descripcion'],
                'monto': monto,
                'esta_pagada': False,
                'id_alquiler': alquiler
            })
            total_multas += monto

        from gestion.models.tipo_dano import TipoDano
        total_danos = 0
        for id_tipo_dano in lista_danos:
            try:
                tipo_dano = TipoDano.objects.get(pk=id_tipo_dano)
                costo = float(tipo_dano.costo_base)
                self.dano_repo.create({
                    'tipo_dano': tipo_dano,
                    'id_alquiler': alquiler
                })
                total_danos += costo
            except TipoDano.DoesNotExist:
                pass

        alquiler.monto_total = float(alquiler.monto_alquiler) + float(recargo_mora) + total_multas + total_danos

        try:
            estado_finalizado = Estado.objects.get(pk=5)
            alquiler.id_estado = estado_finalizado
        except:
            pass

        alquiler.save()

        vehiculo = alquiler.patente_vehiculo
        try:
            if total_danos > 0:
                nuevo_estado_auto = Estado.objects.get(pk=3)  # Mantenimiento
            else:
                nuevo_estado_auto = Estado.objects.get(pk=1)  # Disponible

            vehiculo.id_estado = nuevo_estado_auto
            vehiculo.save()
        except:
            pass

        return {
            "alquiler": alquiler,
            "detalle": {
                "monto_original": float(alquiler.monto_alquiler),
                "recargo_mora": float(recargo_mora),
                "multas": total_multas,
                "danos": total_danos,
                "total_final": alquiler.monto_total
            }
        }

