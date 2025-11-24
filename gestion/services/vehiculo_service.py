from gestion.models import Mantenimiento
from gestion.repositories.vehiculo_repository import VehiculoRepository
from gestion.models.marca import Marca
from gestion.models.estado import Estado
from gestion.models.alquiler import Alquiler
from datetime import datetime, date


class VehiculoService:
    def __init__(self):
        self.repo = VehiculoRepository()

    def listar_vehiculos(self):
        return self.repo.get_all()

    def obtener_opciones_formulario(self):
        return {
            'marcas': Marca.objects.all(),
            'estados': Estado.objects.filter(ambito='VEHICULO')
        }

    def crear_vehiculo(self, patente, modelo, color, precio, marca_nombre, estado_id):
        # --- 1. Validaciones de Negocio ---
        if not patente:
            raise ValueError("La patente es obligatoria.")

        if len(patente) < 6:
            raise ValueError("La patente parece ser demasiado corta.")

        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError("El precio por día debe ser mayor a 0.")
        except ValueError:
            raise ValueError("El precio debe ser un número válido.")

        # Validar duplicados
        if self.repo.get_by_id(patente):
            raise ValueError(f"El vehículo con patente {patente} ya está registrado.")

        # --- 2. Obtención de Instancias (Relaciones FK) ---
        # Django requiere el OBJETO para asignar una ForeignKey, no solo el texto/id.

        # Buscamos la Marca (PK es el nombre según tu DER)
        try:
            marca_instancia = Marca.objects.get(pk=marca_nombre)
        except Marca.DoesNotExist:
            raise ValueError(f"La marca '{marca_nombre}' no existe en la base de datos.")

        # Buscamos el Estado (PK es el id)
        try:
            estado_instancia = Estado.objects.get(pk=estado_id)
        except Estado.DoesNotExist:
            raise ValueError(f"El estado con ID {estado_id} no es válido.")

        # --- 3. Preparación de Datos para el Modelo ---
        # IMPORTANTE: Las claves del dict deben coincidir EXACTAMENTE con los campos del Model Vehiculo
        datos = {
            'patente': patente.upper().strip(),
            'modelo': modelo.strip(),
            'color': color.strip(),
            'precio_x_dia': precio_float,  # Coincide con Model: precio_x_dia
            'nombre_marca': marca_instancia,  # Coincide con Model: nombre_marca (pasamos el objeto)
            'id_estado': estado_instancia  # Coincide con Model: id_estado (pasamos el objeto)
        }

        return self.repo.create(datos)

    def eliminar_vehiculo(self, patente):
        return self.repo.delete(patente)

    def buscar_disponibles_por_fecha(self, fecha_desde_str, fecha_hasta_str):
        """
        Devuelve los vehículos que NO tienen alquileres NI mantenimientos superpuestos en esas fechas.
        """
        # 1. Parsear fechas
        try:
            f_inicio = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")

        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fin.")

        # 1. Encontrar patentes OCUPADAS por ALQUILERES
        alquileres_que_molestan = Alquiler.objects.filter(
            id_estado__in=[4, 7],  # Confirmados o Activos
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).values_list('patente_vehiculo', flat=True)

        # 2. Encontrar patentes OCUPADAS por MANTENIMIENTO
        # Esta es la fuente de verdad para bloqueos por taller.
        mantenimientos_que_molestan = Mantenimiento.objects.filter(
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).values_list('patente', flat=True)

        # 3. EXCLUSIÓN CRÍTICA: VEHÍCULOS EN MORA
        # Buscamos alquileres activos (no finalizados) cuya fecha de fin sea MENOR a hoy.
        # Significa que debían haber vuelto ayer o antes, pero siguen activos.
        # Esos autos NO están disponibles hasta que se regularice la situación.
        patentes_en_mora = Alquiler.objects.filter(
            id_estado__in=[4, 7], # Activos
            fecha_fin__lt=date.today() # Vencidos
        ).values_list('patente_vehiculo', flat=True)

        # 4. Filtrar vehículos
        # Excluimos ambas listas de patentes
        # CORRECCIÓN: Quitamos .exclude(id_estado=3) para permitir reservar autos
        # que hoy están rotos pero estarán sanos en la fecha solicitada.
        disponibles = self.repo.get_all().exclude(
            patente__in=alquileres_que_molestan
        ).exclude(
            patente__in=mantenimientos_que_molestan
        )

        return disponibles