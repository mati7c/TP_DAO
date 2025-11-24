from gestion.repositories.vehiculo_repository import VehiculoRepository
from gestion.models.marca import Marca
from gestion.models.estado import Estado
from gestion.models.alquiler import Alquiler
from datetime import datetime


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
        Devuelve los vehículos que NO tienen alquileres superpuestos en esas fechas.
        """
        # 1. Parsear fechas
        try:
            f_inicio = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")

        if f_inicio > f_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fin.")

        # 2. Encontrar patentes OCUPADAS
        # Un alquiler choca con mi rango si:
        # (Su inicio es antes de mi fin) Y (Su fin es después de mi inicio)
        # Además, solo miramos alquileres Confirmados (4) o Activos (7)
        alquileres_que_molestan = Alquiler.objects.filter(
            id_estado__in=[4, 7],  # Solo los que están vigentes
            fecha_inicio__lte=f_fin,
            fecha_fin__gte=f_inicio
        ).values_list('patente_vehiculo', flat=True)

        # 3. Filtrar vehículos
        # Traemos TODOS los vehículos y EXCLUIMOS las patentes ocupadas
        # También excluimos los que están en mantenimiento (ID 3)
        disponibles = self.repo.get_all().exclude(
            patente__in=alquileres_que_molestan
        ).exclude(
            id_estado=3  # Excluimos los rotos/mantenimiento por seguridad
        )

        return disponibles