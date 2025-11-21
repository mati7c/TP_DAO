from gestion.repositories.empleado_repository import EmpleadoRepository


class EmpleadoService:
    def __init__(self):
        self.repo = EmpleadoRepository()

    def listar_todos(self):
        return self.repo.get_all()

    def crear_empleado(self, dni, nombre, apellido):
        # --- Validaciones ---
        if not dni or not str(dni).isdigit():
            raise ValueError("El DNI debe ser numérico.")

        if not nombre or not apellido:
            raise ValueError("Nombre y Apellido son requeridos.")

        if self.repo.get_by_id(dni):
            raise ValueError("El empleado ya existe.")

        datos = {
            'dni': int(dni),
            'nombre': nombre.strip().title(),
            'apellido': apellido.strip().title()
        }
        return self.repo.create(datos)

    def borrar_empleado(self, dni):
        return self.repo.delete(dni)