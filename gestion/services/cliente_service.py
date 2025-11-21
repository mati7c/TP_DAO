from gestion.repositories.cliente_repository import ClienteRepository


class ClienteService:
    def __init__(self):
        self.repo = ClienteRepository()

    def listar_todos(self):
        return self.repo.get_all()

    def crear_cliente(self, dni, nombre, apellido):
        # --- Validaciones de Negocio ---
        if not dni or not str(dni).isdigit():
            raise ValueError("El DNI debe ser un número válido.")

        if int(dni) < 0:
            raise ValueError("El DNI no puede ser negativo.")

        if not nombre or not apellido:
            raise ValueError("El nombre y el apellido son obligatorios.")

        # Validar si ya existe
        if self.repo.get_by_id(dni):
            raise ValueError("Ya existe un cliente registrado con ese DNI.")

        # Preparar datos para el repo
        datos = {
            'dni': int(dni),
            'nombre': nombre.strip().title(),  # Guardamos con mayúscula inicial
            'apellido': apellido.strip().title()
        }

        return self.repo.create(datos)

    def borrar_cliente(self, dni):
        # Aquí podrías validar si el cliente tiene multas impagas antes de borrar
        return self.repo.delete(dni)