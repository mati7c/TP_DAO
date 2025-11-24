from .persona import Persona


class Empleado(Persona):
    # Aquí solo lo específico de Empleado (si hubiera)
    # legajo = models.CharField(...) # Si quisieras agregar legajo aparte del DNI

    class Meta:
        db_table = 'empleado'