from gestion.models.tipo_dano import TipoDano


class TipoDanoRepository:

    def get_by_id(self, id_tipo):
        try:
            return TipoDano.objects.get(pk=id_tipo)
        except TipoDano.DoesNotExist:
            return None