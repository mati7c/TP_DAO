from gestion.repositories.empleado_repository import EmpleadoRepository
from gestion.factories.persona_factory import PersonaFactory


class EmpleadoService:
    def __init__(self):
        self.repo = EmpleadoRepository()

    def listar_todos(self):
        return self.repo.get_all()

    def crear_empleado(self, dni, nombre, apellido):
        # 1. Validaciones
        if not str(dni).isdigit():
            raise ValueError("El DNI debe ser numérico.")
        if not nombre or not apellido:
            raise ValueError("Nombre y Apellido son requeridos.")

        # Validar existencia previa
        if self.repo.get_by_id(dni):
            raise ValueError("El empleado ya existe.")

        # 2. Preparar diccionario de datos
        datos = {
            'dni': int(dni),
            'nombre': nombre.strip().title(),
            'apellido': apellido.strip().title()
        }

        # 3. USAR LA FACTORY
        # Le pedimos a la fábrica que nos arme el objeto correcto
        nuevo_empleado = PersonaFactory.crear_persona('EMPLEADO', datos)

        # 4. Guardar usando el repositorio actualizado
        return self.repo.save(nuevo_empleado)

    def borrar_empleado(self, dni):
        return self.repo.delete(dni)