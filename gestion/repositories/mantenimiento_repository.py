from gestion.models.mantenimiento import Mantenimiento


class MantenimientoRepository:

    def get_all(self):
        return Mantenimiento.objects.select_related('patente', 'id_tipo_trabajo').all()

    def get_by_id(self, id_mantenimiento):
        try:
            return Mantenimiento.objects.select_related('patente').get(pk=id_mantenimiento)
        except Mantenimiento.DoesNotExist:
            return None

    def create(self, datos):
        return Mantenimiento.objects.create(**datos)

    def save(self, mantenimiento):
        mantenimiento.save()
        return mantenimiento

    def obtener_mantenimientos_activos(self, patente):
        # Busca mantenimientos donde la fecha de fin sea hoy o futuro
        from datetime import date
        return Mantenimiento.objects.filter(patente=patente, fecha_fin__gte=date.today())