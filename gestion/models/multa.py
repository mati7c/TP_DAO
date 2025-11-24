from django.db import models
from .alquiler import Alquiler

class Multa(models.Model):
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    esta_pagada = models.BooleanField(default=False)
    id_alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, db_column='id_alquiler')

    class Meta:
        db_table = 'multa'