from django.shortcuts import render, redirect
from django.contrib import messages
from gestion.services.cliente_service import ClienteService

# Instanciamos el servicio
service = ClienteService()


def listar_clientes(request):
    clientes = service.listar_todos()
    return render(request, 'gestion/clientes/listar.html', {'clientes': clientes})


def crear_cliente(request):
    if request.method == 'POST':
        dni = request.POST['dni']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']

        try:
            service.crear_cliente(dni, nombre, apellido)
            messages.success(request, "Cliente registrado correctamente.")
            return redirect('listar_clientes')

        except ValueError as e:
            # Si el service tira error (ej: DNI repetido), volvemos al form con el mensaje
            messages.error(request, str(e))

    return render(request, 'gestion/clientes/crear.html')


def borrar_cliente(request, dni):
    service.borrar_cliente(dni)
    messages.success(request, "Cliente eliminado.")
    return redirect('listar_clientes')