from django.db import models

class TipoDano(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    costo_base = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'tipodaño' # Aquí sí podemos usar la ñ para que coincida con la BD

    def __str__(self):
        return self.nombre