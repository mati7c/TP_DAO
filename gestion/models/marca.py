from django.db import models

class Marca(models.Model):
    # En el DER, 'nombre' es la PK (está subrayado)
    nombre = models.CharField(max_length=50, primary_key=True)

    class Meta:
        db_table = 'marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre