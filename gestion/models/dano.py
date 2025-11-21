from django.db import models
from .tipo_dano import TipoDano
from .reserva import Reserva

class Dano(models.Model):
    tipo_dano = models.ForeignKey(TipoDano, on_delete=models.PROTECT, db_column='tipo_dano')
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, db_column='id_reserva')

    class Meta:
        db_table = 'daño' # Mapea a la tabla con ñ en la BD