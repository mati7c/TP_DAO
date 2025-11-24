import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.mantenimiento_service import MantenimientoService

service = MantenimientoService()


def listar_mantenimientos(request):
    mants = service.listar_mantenimientos()
    data = []
    for m in mants:
        data.append({
            "id": m.id,
            "patente": m.patente.patente,
            "tipo_trabajo": m.id_tipo_trabajo.nombre,
            "fecha_inicio": m.fecha_inicio,
            "fecha_fin": m.fecha_fin
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def programar_mantenimiento(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            nuevo = service.programar_mantenimiento(
                patente=data['patente'],
                id_tipo_trabajo=data['id_tipo_trabajo'],
                fecha_inicio_str=data['fecha_inicio'],
                fecha_fin_str=data['fecha_fin']
            )

            return JsonResponse({"message": "Mantenimiento programado", "id": nuevo.id}, status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def finalizar_mantenimiento(request, id_mantenimiento):
    if request.method == 'POST':
        try:
            service.finalizar_mantenimiento(id_mantenimiento)
            return JsonResponse({"message": "Mantenimiento finalizado y vehículo liberado."}, status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)

