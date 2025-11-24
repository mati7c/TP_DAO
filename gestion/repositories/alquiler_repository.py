from gestion.models.alquiler import Alquiler


class AlquilerRepository:

    def get_all(self):
        return Alquiler.objects.select_related(
            'dni_cliente', 'dni_empleado', 'patente_vehiculo', 'id_estado'
        ).all()

    def get_by_id(self, id_alquiler):
        try:
            return Alquiler.objects.get(pk=id_alquiler)
        except Alquiler.DoesNotExist:
            return None

    def create(self, datos):
        # Recibe el diccionario ya calculado desde el Service
        return Alquiler.objects.create(**datos)