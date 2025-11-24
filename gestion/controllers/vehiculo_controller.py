import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.vehiculo_service import VehiculoService

service = VehiculoService()


def listar_vehiculos(request):
    vehiculos = service.listar_vehiculos()
    data = []
    for v in vehiculos:
        data.append({
            "patente": v.patente,
            "modelo": v.modelo,
            "color": v.color,
            "marca": v.nombre_marca.nombre,  # Accedemos al atributo del objeto relacionado
            "precio": float(v.precio_x_dia),  # Decimal a Float para JSON
            "estado": v.id_estado.nombre  # Accedemos al atributo del objeto relacionado
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_vehiculo(request):
    if request.method == 'POST':
        try:
            # 1. Parseamos el JSON que viene del Body
            data = json.loads(request.body)

            # 2. Llamamos al servicio pasándole los datos crudos
            nuevo_vehiculo = service.crear_vehiculo(
                patente=data['patente'],
                modelo=data['modelo'],
                color=data['color'],
                precio=data['precio'],  # En el JSON viene como "precio"
                marca_nombre=data['marca'],  # En el JSON viene como "marca" (ej: "Toyota")
                estado_id=data['estado_id']  # En el JSON viene como "estado_id" (ej: 1)
            )

            # 3. Respuesta exitosa
            return JsonResponse({
                "message": "Vehículo creado exitosamente",
                "patente": nuevo_vehiculo.patente
            }, status=201)

        except ValueError as e:
            # Errores de validación (patente corta, precio negativo, marca no existe)
            return JsonResponse({"error": str(e)}, status=400)
        except KeyError as e:
            # Faltan campos en el JSON
            return JsonResponse({"error": f"Falta el campo {str(e)} en el JSON"}, status=400)
        except Exception as e:
            # Errores inesperados
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def borrar_vehiculo(request, patente):
    if request.method in ['DELETE', 'GET']:  # Permitimos GET para facilitar pruebas rápidas
        if service.eliminar_vehiculo(patente):
            return JsonResponse({"message": "Vehículo eliminado"}, status=200)
        return JsonResponse({"error": "No encontrado"}, status=404)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def buscar_vehiculos_disponibles(request):
    """
    Endpoint: /vehiculos/buscar/?desde=2023-12-01&hasta=2023-12-05
    """
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if not desde or not hasta:
        return JsonResponse({"error": "Faltan parámetros 'desde' y 'hasta'"}, status=400)

    try:
        # Llamamos al nuevo método del servicio
        vehiculos = service.buscar_disponibles_por_fecha(desde, hasta)

        # Serializamos la respuesta
        data = []
        for v in vehiculos:
            data.append({
                "patente": v.patente,
                "modelo": v.modelo,
                "marca": v.nombre_marca.nombre,
                "precio": float(v.precio_x_dia),
                "estado_actual": v.id_estado.nombre  # Para info, aunque sabemos que está libre
            })
        return JsonResponse(data, safe=False)

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)