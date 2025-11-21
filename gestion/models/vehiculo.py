from django.db import models
# Importamos las clases relacionadas (usamos string si hay riesgo de import circular, pero aquí es seguro)
from .marca import Marca
from .estado import Estado


class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, primary_key=True)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    precio_x_dia = models.DecimalField(max_digits=10, decimal_places=2)

    # Relaciones (FK)
    nombre_marca = models.ForeignKey(Marca, on_delete=models.PROTECT, db_column='nombre_marca')
    id_estado = models.ForeignKey(Estado, on_delete=models.PROTECT, db_column='id_estado')

    class Meta:
        db_table = 'vehiculo'

    def __str__(self):
        return f"{self.patente} - {self.modelo}"