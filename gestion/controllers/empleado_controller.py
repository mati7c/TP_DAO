from django.shortcuts import render, redirect
from django.contrib import messages
from gestion.services.empleado_service import EmpleadoService

service = EmpleadoService()

def listar_empleados(request):
    empleados = service.listar_todos()
    return render(request, 'gestion/empleados/listar.html', {'empleados': empleados})

def crear_empleado(request):
    if request.method == 'POST':
        try:
            service.crear_empleado(
                dni=request.POST['dni'],
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido']
            )
            messages.success(request, "Empleado registrado correctamente.")
            return redirect('listar_empleados')
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'gestion/empleados/crear.html')

def borrar_empleado(request, dni):
    service.borrar_empleado(dni)
    messages.success(request, "Empleado eliminado.")
    return redirect('listar_empleados')