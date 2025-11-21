from gestion.repositories.vehiculo_repository import VehiculoRepository
from gestion.models.marca import Marca
from gestion.models.estado import Estado


class VehiculoService:
    def __init__(self):
        self.repo = VehiculoRepository()

    def listar_vehiculos(self):
        return self.repo.get_all()

    def obtener_opciones_formulario(self):
        """
        Devuelve las listas necesarias para llenar los <select> del HTML.
        Separamos la lógica de obtención de datos de la vista.
        """
        return {
            'marcas': Marca.objects.all(),
            # Filtramos estados: solo aquellos cuyo ámbito sea 'VEHICULO'
            'estados': Estado.objects.filter(ambito='VEHICULO')
        }

    def crear_vehiculo(self, patente, modelo, color, precio, marca_nombre, estado_id):
        # --- Validaciones ---
        if not patente:
            raise ValueError("La patente es obligatoria.")

        # Validación de formato de patente (ejemplo simple)
        if len(patente) < 6:
            raise ValueError("La patente parece ser demasiado corta.")

        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError("El precio por día debe ser mayor a 0.")
        except ValueError:
            raise ValueError("El precio debe ser un número válido.")

        # Validar que el vehículo no exista ya
        if self.repo.get_by_id(patente):
            raise ValueError(f"El vehículo con patente {patente} ya está registrado.")

        # --- Preparación de Datos ---
        # El repositorio espera los IDs/PKs en el diccionario para buscar las relaciones
        datos = {
            'patente': patente.upper().strip(),
            'modelo': modelo.strip(),
            'color': color.strip(),
            'precio': precio_float,
            'marca_nombre': marca_nombre,  # Clave foránea (nombre)
            'estado_id': estado_id  # Clave foránea (id)
        }

        return self.repo.create(datos)

    def eliminar_vehiculo(self, patente):
        return self.repo.delete(patente)