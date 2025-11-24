import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gestion.services.cliente_service import ClienteService

service = ClienteService()


def listar_clientes(request):
    # Obtenemos los objetos del servicio
    clientes = service.listar_todos()

    # Convertimos los objetos a una lista de diccionarios (JSON no entiende objetos Django)
    data = []
    for c in clientes:
        data.append({
            "dni": c.dni,
            "nombre": c.nombre,
            "apellido": c.apellido
        })

    # safe=False es necesario cuando retornamos una lista, no un dict
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_cliente(request):
    if request.method == 'POST':
        try:
            # 1. LEER EL BODY COMO JSON
            data = json.loads(request.body)

            # 2. LLAMAR AL SERVICIO
            nuevo_cliente = service.crear_cliente(
                dni=data['dni'],
                nombre=data['nombre'],
                apellido=data['apellido']
            )

            # 3. RESPONDER JSON
            return JsonResponse({
                "message": "Cliente creado exitosamente",
                "cliente": {"dni": nuevo_cliente.dni, "apellido": nuevo_cliente.apellido}
            }, status=201)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def borrar_cliente(request, dni):
    if request.method == 'DELETE':  # Idealmente usamos DELETE, no GET
        if service.borrar_cliente(dni):
            return JsonResponse({"message": "Cliente eliminado"}, status=200)
        else:
            return JsonResponse({"error": "Cliente no encontrado"}, status=404)

    # Para compatibilidad si usas GET en postman
    if service.borrar_cliente(dni):
        return JsonResponse({"message": "Cliente eliminado"}, status=200)
    return JsonResponse({"error": "No se pudo eliminar"}, status=400)