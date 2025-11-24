from gestion.models.vehiculo import Vehiculo


class VehiculoRepository:

    def get_all(self):
        # Optimización: Trae la marca y el estado en la misma consulta
        return Vehiculo.objects.select_related('nombre_marca', 'id_estado').all()

    def get_by_id(self, patente):
        try:
            return Vehiculo.objects.select_related('nombre_marca', 'id_estado').get(pk=patente)
        except Vehiculo.DoesNotExist:
            return None

    def create(self, datos):
        # 'datos' debe tener las claves exactas del modelo:
        # patente, modelo, color, precio_x_dia, nombre_marca (objeto), id_estado (objeto)
        return Vehiculo.objects.create(**datos)

    def delete(self, patente):
        vehiculo = self.get_by_id(patente)
        if vehiculo:
            vehiculo.delete()
            return True
        return False

    # Método para reportes filtrados
    def get_by_estado(self, estado_id):
        return Vehiculo.objects.filter(id_estado=estado_id)