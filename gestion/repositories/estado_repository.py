from gestion.models.estado import Estado


class EstadoRepository:

    def get_by_id(self, id_estado):
        try:
            return Estado.objects.get(pk=id_estado)
        except Estado.DoesNotExist:
            return None

    def get_by_nombre(self, nombre):
        try:
            return Estado.objects.get(nombre=nombre)
        except Estado.DoesNotExist:
            return None