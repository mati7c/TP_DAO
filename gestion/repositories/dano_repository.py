from gestion.models.dano import Dano


class DanoRepository:

    def create(self, datos):
        """
        Registra un daño asociado a un alquiler.
        Datos esperados: tipo_dano (objeto), id_alquiler (objeto)
        """
        return Dano.objects.create(**datos)

    def get_by_alquiler(self, id_alquiler):
        return Dano.objects.filter(id_alquiler=id_alquiler)