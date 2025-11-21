from django.db import models

class Cliente(models.Model):
    # DNI como Primary Key
    dni = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    class Meta:
        db_table = 'cliente'

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"