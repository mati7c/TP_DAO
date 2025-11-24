from datetime import datetime, date

from gestion.models import Alquiler, Mantenimiento
from gestion.repositories.alquiler_repository import AlquilerRepository
from gestion.repositories.dano_repository import DanoRepository
from gestion.repositories.multa_repository import MultaRepository
from gestion.repositories.estado_repository import EstadoRepository
from gestion.repositories.tipo_dano_repository import TipoDanoRepository
from gestion.models.cliente import Cliente
from gestion.models.empleado import Empleado
from gestion.models.vehiculo import Vehiculo
from gestion.models.estado import Estado


class AlquilerService:
    def __init__(self):
        self.repo = AlquilerRepository()
        self.dano_repo = DanoRepository()
        self.multa_repo = MultaRepository()
        self.estado_repo = EstadoRepository()
        self.tipo_dano_repo = TipoDanoRepository()

    def listar_alquileres(self):
        return self.repo.get_all()

    def registrar_alquiler(self, dni_cliente, dni_empleado, patente, fecha_inicio_str, fecha_fin_str):
        # --- 1. Conversión de Fechas ---
        try:
            f_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")

        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fecha de fin.")

        if f_inicio < date.today():
            raise ValueError("No se puede registrar un alquiler en el pasado.")

        delta = f_fin - f_inicio
        dias_calculados = delta.days
        if dias_calculados == 0: dias_calculados = 1

        # --- 2. Obtener Instancias ---
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

        # --- 3. VALIDACIONES DE DISPONIBILIDAD ---

        # A) Estado actual crítico: Si HOY está roto, no alquilamos.
        if vehiculo.id_estado.id == 3:
            raise ValueError("El vehículo está actualmente en mantenimiento y no puede ser alquilado.")

        # B) Colisión con Mantenimientos Programados
        colision_mantenimiento = Mantenimiento.objects.filter(
            patente=patente,
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colision_mantenimiento:
            raise ValueError(f"El vehículo {patente} tiene mantenimiento programado en esas fechas.")

        # C) Colisión con Alquileres Existentes
        colisiones_alquiler = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],  # Confirmado o Activo
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).exists()

        if colisiones_alquiler:
            raise ValueError(f"El vehículo {patente} ya tiene una reserva en esas fechas.")

        # D) EXCLUSIÓN POR MORA
        mora_activa = Alquiler.objects.filter(
            patente_vehiculo=patente,
            id_estado__in=[4, 7],
            fecha_fin__lt=date.today()
        ).exists()

        if mora_activa:
            raise ValueError(f"El vehículo {patente} tiene un alquiler previo vencido (Mora).")

        # --- 4. Guardado con Estado Dinámico ---
        # Lógica: Si empieza HOY, es Activo (7). Si es futuro, es Confirmado (4).
        if f_inicio == date.today():
            id_estado_inicial = 7
        else:
            id_estado_inicial = 4

        try:
            estado_inicial = Estado.objects.get(pk=id_estado_inicial)
        except Estado.DoesNotExist:
            raise ValueError(f"El estado inicial (ID {id_estado_inicial}) no existe en la BD.")

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
            'id_estado': estado_inicial
        }

        nuevo_alquiler = self.repo.create(datos)

        # --- 5. Actualizar Estado del Vehículo (Solo si empieza HOY) ---
        if f_inicio == date.today():
            try:
                estado_alquilado = Estado.objects.get(pk=2)  # ID 2 = Alquilado
                vehiculo.id_estado = estado_alquilado
                vehiculo.save()
            except:
                pass

        return nuevo_alquiler

    def finalizar_alquiler(self, id_alquiler):
        """
        Cierra un alquiler usando la fecha de HOY.
        Calcula mora automáticamente.
        Suma multas y daños YA CARGADOS previamente en la base de datos asociados a este alquiler.
        """
        # --- 1. Obtener y Validar Alquiler ---
        alquiler = self.repo.get_by_id(id_alquiler)
        if not alquiler:
            raise ValueError(f"No se encontró el alquiler con ID {id_alquiler}.")

        # Validamos por ID (5 = Finalizado)
        if alquiler.id_estado.id == 5:
            raise ValueError("Este alquiler ya se encuentra finalizado.")

        # --- 2. Definir Fecha de Devolución (HOY) ---
        f_devolucion = date.today()

        # Validación de seguridad: no cerrar antes de empezar
        if f_devolucion < alquiler.fecha_inicio:
            raise ValueError(
                f"No se puede finalizar el alquiler antes de su fecha de inicio ({alquiler.fecha_inicio}).")

        # --- 3. Calcular Mora ---
        recargo_mora = 0.0
        if f_devolucion > alquiler.fecha_fin:
            dias_extra = (f_devolucion - alquiler.fecha_fin).days
            precio_dia = float(alquiler.patente_vehiculo.precio_x_dia)

            # REGLA DE NEGOCIO: Se cobra el doble por cada día de retraso
            recargo_mora = dias_extra * precio_dia * 2

        # --- 4. Buscar Multas Existentes ---
        # Usamos el repositorio para buscar lo que ya se cargó en BD
        multas_cargadas = self.multa_repo.get_by_alquiler(alquiler)

        total_multas = 0.0
        for m in multas_cargadas:
            total_multas += float(m.monto)

        # --- 5. Buscar Daños Existentes ---
        # Usamos el repositorio para buscar lo que ya se cargó en BD
        danos_cargados = self.dano_repo.get_by_alquiler(alquiler)

        total_danos = 0.0
        for d in danos_cargados:
            # Accedemos al costo base a través de la relación con TipoDano
            total_danos += float(d.tipo_dano.costo_base)

        # --- 6. Actualizar Totales y Cerrar Alquiler ---
        monto_original = float(alquiler.monto_alquiler)
        alquiler.monto_total = monto_original + recargo_mora + total_multas + total_danos

        # Opcional: Guardar la fecha real de fin si quisieras tener el dato histórico exacto
        # alquiler.fecha_fin = f_devolucion

        # Cambiar estado a Finalizado (ID 5)
        estado_finalizado = self.estado_repo.get_by_id(5)
        if not estado_finalizado:
            raise ValueError("Estado 'Finalizado' (ID 5) no existe.")

        alquiler.id_estado = estado_finalizado
        alquiler.save()

        # --- 7. Liberar Vehículo (Gestión de Estado) ---
        vehiculo = alquiler.patente_vehiculo

        # Lógica inteligente: Si hubo daños registrados, el auto va a Taller.
        if len(danos_cargados) > 0:
            nuevo_estado = self.estado_repo.get_by_id(3)  # ID 3 = En Mantenimiento
        else:
            nuevo_estado = self.estado_repo.get_by_id(1)  # ID 1 = Disponible

        if nuevo_estado:
            vehiculo.id_estado = nuevo_estado
            vehiculo.save()

        # --- 8. Retornar Resumen ---
        return {
            "alquiler": alquiler,
            "detalle": {
                "fecha_devolucion": f_devolucion,
                "monto_original": monto_original,
                "recargo_mora": recargo_mora,
                "cant_multas": len(multas_cargadas),
                "total_multas": total_multas,
                "cant_danos": len(danos_cargados),
                "total_danos": total_danos,
                "total_final": alquiler.monto_total,
                "nuevo_estado_vehiculo": vehiculo.id_estado.nombre
            }
        }

    def iniciar_alquiler(self, id_alquiler):
        """
        Transforma una reserva 'Confirmada' en un alquiler 'Activo' cuando el cliente retira el auto.
        """
        alquiler = self.repo.get_by_id(id_alquiler)
        if not alquiler:
            raise ValueError("Alquiler no encontrado.")

        # Validar Fecha: No entregar antes de tiempo
        if alquiler.fecha_inicio > date.today():
            raise ValueError(f"No se puede iniciar el alquiler antes de la fecha pactada ({alquiler.fecha_inicio}).")

        # Validar Estado del Alquiler
        # Solo iniciamos si está 'Confirmado' (4). Si ya está 'Activo' (7), no hacemos nada (idempotencia).
        if alquiler.id_estado.id == 7:
            return alquiler  # Ya estaba activo

        if alquiler.id_estado.id != 4:
            raise ValueError("El alquiler no está en estado 'Confirmado' para poder iniciarse.")

        # --- ACCIONES ---

        # 1. Pasar Alquiler a 'Activo' (7)
        try:
            estado_activo = Estado.objects.get(pk=7)
            alquiler.id_estado = estado_activo
            alquiler.save()
        except Estado.DoesNotExist:
            raise ValueError("Estado 'Activo' (ID 7) no existe.")

        # 2. Pasar Vehículo a 'Alquilado' (2)
        vehiculo = alquiler.patente_vehiculo

        # Validar que el auto no esté ocupado por error (aunque el filtro de fechas debería haberlo prevenido)
        if vehiculo.id_estado.id not in [1, 2]:  # 1=Disponible, 2=Ya alquilado (por si acaso)
            # Nota: Si estaba en mantenimiento (3), esto saltaría.
            pass

        try:
            estado_alquilado = Estado.objects.get(pk=2)
            vehiculo.id_estado = estado_alquilado
            vehiculo.save()
        except Estado.DoesNotExist:
            raise ValueError("Estado 'Alquilado' (ID 2) no existe.")

        return alquiler

    def registrar_multa(self, id_alquiler, descripcion, monto):
        """
        Agrega una multa a un alquiler en curso.
        """
        alquiler = self.repo.get_by_id(id_alquiler)
        if not alquiler:
            raise ValueError("Alquiler no encontrado.")

        if alquiler.id_estado.id == 5:  # Finalizado
            raise ValueError("No se pueden agregar multas a un alquiler finalizado.")

        if float(monto) <= 0:
            raise ValueError("El monto de la multa debe ser mayor a 0.")

        nueva_multa = self.multa_repo.create({
            'descripcion': descripcion,
            'monto': monto,
            'esta_pagada': False,
            'id_alquiler': alquiler
        })
        return nueva_multa

    def registrar_dano(self, id_alquiler, id_tipo_dano, observaciones=""):
        """
        Agrega un daño a un alquiler en curso.
        """
        alquiler = self.repo.get_by_id(id_alquiler)
        if not alquiler:
            raise ValueError("Alquiler no encontrado.")

        if alquiler.id_estado.id == 5:  # Finalizado
            raise ValueError("No se pueden agregar daños a un alquiler finalizado.")

        tipo_dano = self.tipo_dano_repo.get_by_id(id_tipo_dano)
        if not tipo_dano:
            raise ValueError(f"El tipo de daño ID {id_tipo_dano} no existe.")

        nuevo_dano = self.dano_repo.create({
            'tipo_dano': tipo_dano,
            'id_alquiler': alquiler
            # Si tu modelo Dano tuviera un campo 'observaciones', lo pasaríamos aquí.
            # Por ahora tu modelo Dano solo tiene FKs según lo que vimos antes.
        })
        return nuevo_dano