from django.db import models
from .reserva import Reserva

class Multa(models.Model):
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    esta_pagada = models.BooleanField(default=False)
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, db_column='id_reserva')

    class Meta:
        db_table = 'multa'