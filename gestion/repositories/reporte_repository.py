from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth

from gestion.models.alquiler import Alquiler


class ReporteRepository:

    def obtener_historial_por_cliente(self, dni_cliente):
        """
        Busca todos los alquileres de un cliente específico.
        Optimiza la consulta trayendo el vehículo, la marca y el estado en un solo viaje a la BD.
        """
        return Alquiler.objects.filter(dni_cliente=dni_cliente).select_related(
            'patente_vehiculo',
            'patente_vehiculo__nombre_marca',  # Para mostrar la marca (Toyota)
            'id_estado'
        ).order_by('-fecha_inicio')  # Orden descendente (el más reciente primero)

    def obtener_ranking_vehiculos(self, top=5):
        """
        Agrupa los alquileres por vehículo y cuenta cuántas veces se alquiló cada uno.
        Retorna un QuerySet de diccionarios.
        """
        return Alquiler.objects.values(
            'patente_vehiculo__patente',
            'patente_vehiculo__modelo',
            'patente_vehiculo__nombre_marca__nombre'
        ).annotate(
            cantidad_alquileres=Count('id')
        ).order_by('-cantidad_alquileres')[:top]

    def obtener_alquileres_por_periodo(self, f_desde, f_hasta):
        """
        Filtra alquileres que hayan iniciado dentro del rango de fechas.
        """
        return Alquiler.objects.filter(
            fecha_inicio__gte=f_desde,
            fecha_inicio__lte=f_hasta
        ).select_related('dni_cliente', 'patente_vehiculo')

    def obtener_facturacion_mensual(self, anio):
        """
        Suma el 'monto_total' agrupado por mes para un año específico.
        """
        return Alquiler.objects.filter(
            fecha_inicio__year=anio
        ).annotate(
            mes=ExtractMonth('fecha_inicio')
        ).values('mes').annotate(
            total_facturado=Sum('monto_total')
        ).order_by('mes')