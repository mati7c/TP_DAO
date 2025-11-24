import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.alquiler_service import AlquilerService

service = AlquilerService()


def listar_alquileres(request):
    alquileres = service.listar_alquileres()
    data = []
    for a in alquileres:
        data.append({
            "id": a.id,
            "cliente": f"{a.dni_cliente.nombre} {a.dni_cliente.apellido}",
            "empleado": f"{a.dni_empleado.nombre} {a.dni_empleado.apellido}",
            "vehiculo": a.patente_vehiculo.modelo,
            "desde": a.fecha_inicio,
            "hasta": a.fecha_fin,
            "total": float(a.monto_total),
            "estado": a.id_estado.nombre
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_alquiler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            nuevo_alquiler = service.registrar_alquiler(
                dni_cliente=data['dni_cliente'],
                dni_empleado=data['dni_empleado'],
                patente=data['patente'],
                fecha_inicio_str=data['fecha_inicio'],  # Ej: "2023-11-23"
                fecha_fin_str=data['fecha_fin']
            )

            return JsonResponse({
                "message": "Alquiler registrado exitosamente",
                "id_alquiler": nuevo_alquiler.id,
                "monto": float(nuevo_alquiler.monto_total)
            }, status=201)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def iniciar_alquiler(request, id_alquiler):
    if request.method == 'POST':
        try:
            # Llamamos al servicio para cambiar el estado a 'Alquilado' (entrega de llaves)
            service.iniciar_alquiler(id_alquiler)

            return JsonResponse({
                "message": "Vehículo entregado. Estado actualizado a Alquilado.",
                "id_alquiler": id_alquiler
            }, status=200)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def finalizar_alquiler(request, id_alquiler):
    """
    Endpoint para cerrar el alquiler.
    NO recibe JSON. Calcula todo automáticamente basándose en el ID y la fecha de hoy.
    """
    if request.method == 'POST':
        try:
            # Llamada simplificada: Solo pasamos el ID
            resultado = service.finalizar_alquiler(id_alquiler)

            return JsonResponse({
                "message": "Alquiler finalizado correctamente",
                "detalle_cobro": resultado['detalle']
            }, status=200)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)