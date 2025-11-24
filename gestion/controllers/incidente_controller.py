import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.alquiler_service import AlquilerService


service = AlquilerService()

@csrf_exempt
def cargar_multa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            multa = service.registrar_multa(
                id_alquiler=data['id_alquiler'],
                descripcion=data['descripcion'],
                monto=data['monto']
            )

            return JsonResponse({
                "message": "Multa registrada correctamente",
                "id_multa": multa.id
            }, status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)



@csrf_exempt
def cargar_dano(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            dano = service.registrar_dano(
                id_alquiler=data['id_alquiler'],
                id_tipo_dano=data['id_tipo_dano']
            )

            return JsonResponse({
                "message": "Daño registrado correctamente",
                "id_dano": dano.id,
                "tipo": dano.tipo_dano.nombre
            }, status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)