from gestion.models.cliente import Cliente
from gestion.models.empleado import Empleado


class PersonaFactory:

    @staticmethod
    def crear_persona(tipo, datos):
        """
        Método estático que fabrica la instancia correcta.
        :param tipo: str ('CLIENTE' o 'EMPLEADO')
        :param datos: dict con dni, nombre, apellido
        """
        tipo = tipo.upper()

        if tipo == 'CLIENTE':
            return Cliente(**datos)

        elif tipo == 'EMPLEADO':
            return Empleado(**datos)

        else:
            raise ValueError(f"El tipo de persona '{tipo}' no es válido.")