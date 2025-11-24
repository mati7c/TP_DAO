from gestion.repositories.cliente_repository import ClienteRepository
from gestion.factories.persona_factory import PersonaFactory # Importamos la Factory


class ClienteService:
    def __init__(self):
        self.repo = ClienteRepository()

    def listar_todos(self):
        return self.repo.get_all()

    def crear_cliente(self, dni, nombre, apellido):
        # 1. Validaciones (Igual que antes)
        if not str(dni).isdigit(): raise ValueError("DNI inválido")
        # ... otras validaciones ...

        # 2. Preparar datos
        datos = {
            'dni': int(dni),
            'nombre': nombre,
            'apellido': apellido
        }

        # 3. PATRÓN FACTORY: La fábrica crea la instancia (en memoria)
        nuevo_cliente = PersonaFactory.crear_persona('CLIENTE', datos)

        # 4. PERSISTENCIA: El repositorio guarda esa instancia en la BD
        return self.repo.save(nuevo_cliente)

    def borrar_cliente(self, dni):
        # Aquí podrías validar si el cliente tiene multas impagas antes de borrar
        return self.repo.delete(dni)