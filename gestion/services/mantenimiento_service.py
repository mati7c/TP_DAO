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
            f_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido (AAAA-MM-DD)")

        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser posterior al fin.")

        if f_inicio < date.today():
            raise ValueError("No se puede programar mantenimiento en el pasado.")

        # --- 2. Validar Existencias ---
        try:
            vehiculo = Vehiculo.objects.get(pk=patente)
        except Vehiculo.DoesNotExist:
            raise ValueError(f"El vehículo {patente} no existe.")

        try:
            tipo_trabajo = TipoTrabajo.objects.get(pk=id_tipo_trabajo)
        except TipoTrabajo.DoesNotExist:
            raise ValueError("Tipo de trabajo inválido.")

        # --- 3. VALIDACIÓN DE COLISIÓN (Crucial) ---
        # Verificamos si hay ALQUILERES confirmados/activos en esas fechas
        colision_alquiler = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],  # Confirmado o Activo
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colision_alquiler:
            raise ValueError(f"El vehículo tiene alquileres confirmados en esas fechas.")

        # Verificamos si hay OTROS MANTENIMIENTOS en esas fechas
        from gestion.models.mantenimiento import Mantenimiento
        colision_mantenimiento = Mantenimiento.objects.filter(
            patente=patente,
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colision_mantenimiento:
            raise ValueError(f"El vehículo ya tiene otro mantenimiento en esas fechas.")

        # --- 4. Crear Mantenimiento ---
        datos = {
            'fecha_inicio': f_inicio,
            'fecha_fin': f_fin,
            'patente': vehiculo,
            'id_tipo_trabajo': tipo_trabajo
        }
        nuevo_mantenimiento = self.repo.create(datos)

        # --- 5. Actualizar Estado del Vehículo ---
        # Si el mantenimiento empieza HOY, cambiamos el estado ya mismo.
        # Si es futuro, el estado cambiará el día que corresponda (o manualmente).
        if f_inicio == date.today():
            try:
                estado_mantenimiento = Estado.objects.get(pk=3)  # ID 3 = En Mantenimiento
                vehiculo.id_estado = estado_mantenimiento
                vehiculo.save()
            except:
                pass  # Si falla el estado, el mantenimiento igual se creó (bloqueo por fechas)

        return nuevo_mantenimiento

    def finalizar_mantenimiento(self, id_mantenimiento):
        mantenimiento = self.repo.get_by_id(id_mantenimiento)
        if not mantenimiento:
            raise ValueError("Mantenimiento no encontrado.")

        # --- 1. Ajustar fecha fin a HOY ---
        mantenimiento.fecha_fin = date.today()
        self.repo.save(mantenimiento)

        # --- 2. Liberar Vehículo (Disponible) ---
        vehiculo = mantenimiento.patente
        try:
            estado_disponible = Estado.objects.get(pk=1)  # ID 1 = Disponible
            vehiculo.id_estado = estado_disponible
            vehiculo.save()
        except:
            raise ValueError("Error al actualizar estado del vehículo.")

        return mantenimiento