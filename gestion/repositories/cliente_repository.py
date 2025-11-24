from gestion.models.cliente import Cliente


class ClienteRepository:

    def get_all(self):
        # Retorna todos los clientes ordenados por apellido
        return Cliente.objects.all().order_by('apellido')

    def get_by_id(self, dni):
        # Busca por DNI (que es la PK)
        try:
            return Cliente.objects.get(pk=dni)
        except Cliente.DoesNotExist:
            return None

    def save(self, cliente_instance):
        # Recibe el OBJETO ya creado por la fábrica y lo guarda
        cliente_instance.save()
        return cliente_instance

    def update(self, dni, nuevos_datos):
        cliente = self.get_by_id(dni)
        if cliente:
            # Actualizamos solo los campos que vienen en el diccionario
            for key, value in nuevos_datos.items():
                setattr(cliente, key, value)
            cliente.save()
            return cliente
        return None

    def delete(self, dni):
        cliente = self.get_by_id(dni)
        if cliente:
            cliente.delete()
            return True
        return False