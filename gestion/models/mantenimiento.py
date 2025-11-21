from django.db import models
from .vehiculo import Vehiculo
from .tipo_trabajo import TipoTrabajo

class Mantenimiento(models.Model):
    fecha = models.DateField()
    patente = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, db_column='patente')
    id_tipo_trabajo = models.ForeignKey(TipoTrabajo, on_delete=models.PROTECT, db_column='id_tipo_trabajo')

    class Meta:
        db_table = 'mantenimiento'