from datetime import datetime, date
from django.db.models import Q
from gestion.repositories.mantenimiento_repository import MantenimientoRepository
from gestion.models.vehiculo import Vehiculo
from gestion.models.tipo_trabajo import TipoTrabajo
from gestion.models.estado import Estado
from gestion.models.alquiler import Alquiler


class MantenimientoService:
    def __init__(self):
        self.repo = MantenimientoRepository()

    def listar_mantenimientos(self):
        return self.repo.get_all()

    def programar_mantenimiento(self, patente, id_tipo_trabajo, fecha_inicio_str, fecha_fin_str):
        # --- 1. Validar Fechas ---
        try:
            # Forzamos que la fecha de inicio sea HOY, ignorando lo que venga del str si se desea
            # O validamos que el str sea hoy.
            # Según tu pedido: "solo se va a poder programar para que empiece hoy"
            f_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()

            if f_inicio != date.today():
                raise ValueError(f"El mantenimiento debe iniciar hoy ({date.today()}).")

            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido (AAAA-MM-DD)")

        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser posterior al fin.")

        # --- 2. Validar Existencias ---
        try:
            vehiculo = Vehiculo.objects.get(pk=patente)
        except Vehiculo.DoesNotExist:
            raise ValueError(f"El vehículo {patente} no existe.")

        try:
            tipo_trabajo = TipoTrabajo.objects.get(pk=id_tipo_trabajo)
        except TipoTrabajo.DoesNotExist:
            raise ValueError("Tipo de trabajo inválido.")

        # --- 3. VALIDACIONES DE DISPONIBILIDAD ---

        # A) Verificar si el auto está ALQUILADO actualmente
        # Si está en estado 'Alquilado' (2), no está en el taller.
        if vehiculo.id_estado.id == 2:
            raise ValueError("El vehículo está actualmente alquilado. Debe finalizar el alquiler primero.")

        # B) Verificar MORA (Alquileres vencidos no devueltos)
        # Buscamos alquileres activos cuya fecha de fin ya pasó.
        mora_activa = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],  # Activos
            fecha_fin__lt=date.today()
        ).exists()

        if mora_activa:
            raise ValueError("El vehículo tiene un alquiler en mora (no devuelto). No se puede enviar a mantenimiento.")

        # C) Verificar colisión con MANTENIMIENTOS existentes
        # (Por si ya había uno cargado para hoy)
        colision_mantenimiento = self.repo.obtener_mantenimientos_activos(patente).exists()
        if colision_mantenimiento:
            raise ValueError(f"El vehículo ya se encuentra en mantenimiento.")

        # --- 4. Crear Mantenimiento ---
        datos = {
            'fecha_inicio': f_inicio,
            'fecha_fin': f_fin,
            'patente': vehiculo,
            'id_tipo_trabajo': tipo_trabajo
        }
        nuevo_mantenimiento = self.repo.create(datos)

        # --- 5. Actualizar Estado del Vehículo ---
        # Como empieza HOY sí o sí, cambiamos el estado inmediatamente.
        try:
            estado_mantenimiento = Estado.objects.get(pk=3)  # ID 3 = En Mantenimiento
            vehiculo.id_estado = estado_mantenimiento
            vehiculo.save()
        except:
            pass

        return nuevo_mantenimiento

    def finalizar_mantenimiento(self, id_mantenimiento):
        mantenimiento = self.repo.get_by_id(id_mantenimiento)
        if not mantenimiento:
            raise ValueError("Mantenimiento no encontrado.")

        # --- 1. Validar Fecha de Finalización ---
        # Regla: "solo se va a poder finalizar el dia de fecha:fin automaticamente"
        hoy = date.today()

        if hoy != mantenimiento.fecha_fin:
            raise ValueError(f"No se puede finalizar antes de la fecha pactada ({mantenimiento.fecha_fin}).")

        # Opcional: Si quieres ser estricto y que solo se finalice EL DIA exacto:
        # if hoy != mantenimiento.fecha_fin: raise ValueError(...)
        # Pero usualmente permitimos finalizarlo si ya pasó la fecha (hoy >= fin).

        # --- 2. Liberar Vehículo (Disponible) ---
        vehiculo = mantenimiento.patente
        try:
            estado_disponible = Estado.objects.get(pk=1)  # ID 1 = Disponible
            vehiculo.id_estado = estado_disponible
            vehiculo.save()
        except:
            raise ValueError("Error al actualizar estado del vehículo.")

        return mantenimiento