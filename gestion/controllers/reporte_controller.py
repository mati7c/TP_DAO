from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view # Útil si usas Swagger, sino es opcional
from gestion.services.reporte_service import ReporteService

service = ReporteService()

@api_view(['GET']) # Decorador para que aparezca en Swagger si lo tienes activo
def reporte_historial_cliente(request, dni):
    """
    Endpoint: GET /reportes/cliente/<dni>/
    Devuelve el historial completo y estadísticas de un cliente.
    """
    try:
        data = service.obtener_reporte_cliente(dni)
        return JsonResponse(data, safe=False)

    except ValueError as e:
        # Cliente no encontrado
        return JsonResponse({"error": str(e)}, status=404)

    except Exception as e:
        # Error inesperado de base de datos
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


@api_view(['GET'])
def reporte_ranking_vehiculos(request):
    """
    Endpoint: GET /reportes/ranking/
    Devuelve los 5 vehículos con más alquileres históricos.
    """
    try:
        # Podrías recibir el parámetro 'top' por URL si quisieras hacerlo dinámico
        # top = int(request.GET.get('top', 5))

        ranking = service.ranking_vehiculos()  # Usamos el default de 5
        return JsonResponse(ranking, safe=False)

    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


@api_view(['GET'])  # Mantengo @api_view si tienes DRF instalado, si no quítalo
def reporte_alquileres_periodo(request):
    """
    Endpoint: /reportes/periodo/?desde=2023-01-01&hasta=2023-12-31
    """
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if not desde or not hasta:
        return JsonResponse({"error": "Faltan parámetros 'desde' y 'hasta' en la URL"}, status=400)

    try:
        reporte = service.alquileres_periodo(desde, hasta)
        return JsonResponse(reporte, safe=False)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


@api_view(['GET'])
def reporte_facturacion_mensual(request):
    """
    Endpoint: /reportes/facturacion/?anio=2023
    Ideal para gráfico de barras.
    """
    anio = request.GET.get('anio')

    # Si no mandan año, usamos el actual por defecto
    if not anio:
        from datetime import date
        anio = date.today().year

    try:
        stats = service.facturacion_mensual(anio)
        return JsonResponse(stats, safe=False)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)