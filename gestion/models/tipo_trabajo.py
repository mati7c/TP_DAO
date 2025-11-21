from django.db import models

class TipoTrabajo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tipotrabajo'

    def __str__(self):
        return self.nombre