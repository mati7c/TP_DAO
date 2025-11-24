from django.db import models

class Persona(models.Model):
    """
    Clase abstracta que define los atributos comunes.
    No genera tabla en BD, pero sus hijos sí.
    """
    dni = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    class Meta:
        abstract = True  # Clave para la herencia en Django

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"