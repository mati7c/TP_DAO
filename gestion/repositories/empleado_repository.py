from gestion.models.empleado import Empleado

class EmpleadoRepository:

    def get_all(self):
        return Empleado.objects.all().order_by('apellido')

    def get_by_id(self, dni):
        try:
            return Empleado.objects.get(pk=dni)
        except Empleado.DoesNotExist:
            return None

    def create(self, datos):
        return Empleado.objects.create(**datos)

    def update(self, dni, nuevos_datos):
        empleado = self.get_by_id(dni)
        if empleado:
            for key, value in nuevos_datos.items():
                setattr(empleado, key, value)
            empleado.save()
            return empleado
        return None

    def delete(self, dni):
        empleado = self.get_by_id(dni)
        if empleado:
            empleado.delete()
            return True
        return False