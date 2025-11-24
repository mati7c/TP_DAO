from gestion.models.multa import Multa


class MultaRepository:

    def create(self, datos):
        """
        Crea una multa asociada a un alquiler.
        Datos esperados: descripcion, monto, esta_pagada, id_alquiler (objeto)
        """
        return Multa.objects.create(**datos)

    def get_by_alquiler(self, id_alquiler):
        return Multa.objects.filter(id_alquiler=id_alquiler)