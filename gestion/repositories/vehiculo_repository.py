from gestion.models.vehiculo import Vehiculo

class VehiculoRepository:

    def get_all(self):
        # select_related optimiza la consulta trayendo los datos de las FK
        return Vehiculo.objects.select_related('nombre_marca', 'id_estado').all()

    def get_by_id(self, patente):
        try:
            # También usamos select_related aquí por si necesitamos mostrar la marca/estado
            return Vehiculo.objects.select_related('nombre_marca', 'id_estado').get(pk=patente)
        except Vehiculo.DoesNotExist:
            return None

    def create(self, datos):
        # datos debe contener las instancias de Marca y Estado, no solo los IDs strings.
        # Esto se maneja en la capa de Service.
        return Vehiculo.objects.create(**datos)

    def update(self, patente, nuevos_datos):
        vehiculo = self.get_by_id(patente)
        if vehiculo:
            for key, value in nuevos_datos.items():
                setattr(vehiculo, key, value)
            vehiculo.save()
            return vehiculo
        return None

    def delete(self, patente):
        vehiculo = self.get_by_id(patente)
        if vehiculo:
            vehiculo.delete()
            return True
        return False

    # Métodos extra útiles para filtros (citado en requerimientos de reportes [cite: 30])
    def get_by_estado(self, estado_id):
        return Vehiculo.objects.filter(id_estado=estado_id)