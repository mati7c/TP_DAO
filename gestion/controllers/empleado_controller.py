import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.empleado_service import EmpleadoService

service = EmpleadoService()


def listar_empleados(request):
    # Obtenemos la lista de objetos del servicio
    empleados = service.listar_todos()

    # Serializamos a JSON
    data = []
    for e in empleados:
        data.append({
            "dni": e.dni,
            "nombre": e.nombre,
            "apellido": e.apellido
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_empleado(request):
    if request.method == 'POST':
        try:
            # 1. Leer JSON del Body
            data = json.loads(request.body)

            # 2. Llamar al servicio
            nuevo_empleado = service.crear_empleado(
                dni=data['dni'],
                nombre=data['nombre'],
                apellido=data['apellido']
            )

            # 3. Respuesta exitosa
            return JsonResponse({
                "message": "Empleado creado exitosamente",
                "empleado": {
                    "dni": nuevo_empleado.dni,
                    "nombre": nuevo_empleado.nombre,
                    "apellido": nuevo_empleado.apellido
                }
            }, status=201)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error del servidor: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def borrar_empleado(request, dni):
    # Soporta tanto DELETE como GET para facilitar pruebas simples
    if service.borrar_empleado(dni):
        return JsonResponse({"message": "Empleado eliminado correctamente"}, status=200)

    return JsonResponse({"error": "Empleado no encontrado"}, status=404)