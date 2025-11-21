from django.db import models

class Estado(models.Model):
    # ID autoincremental por defecto en Django
    nombre = models.CharField(max_length=50, unique=True)
    ambito = models.CharField(max_length=50) # Ej: 'VEHICULO', 'RESERVA'

    class Meta:
        db_table = 'estado'

    def __str__(self):
        return f"{self.nombre} ({self.ambito})"