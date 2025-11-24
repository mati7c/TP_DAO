from .persona import Persona


class Cliente(Persona):
    # Aquí solo pones lo específico de Cliente (si hubiera)
    # Por ejemplo:
    # fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'cliente'