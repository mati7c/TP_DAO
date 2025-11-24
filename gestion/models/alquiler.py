from django.db import models
from .empleado import Empleado
from .cliente import Cliente
from .vehiculo import Vehiculo
from .estado import Estado


class Alquiler(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_alquiler = models.DecimalField(max_digits=12, decimal_places=2)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    dias_alquiler = models.IntegerField()

    # Claves Foráneas (Respetando nombres de columnas del DER)
    dni_empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, db_column='dni_empleado')
    dni_cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, db_column='dni_cliente')
    patente_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, db_column='patente_vehiculo')
    id_estado = models.ForeignKey(Estado, on_delete=models.PROTECT, db_column='id_estado')

    class Meta:
        db_table = 'alquiler'

    def __str__(self):
        return f"Alquiler #{self.id} - {self.dni_cliente}"