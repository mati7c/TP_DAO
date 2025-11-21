from django.shortcuts import render, redirect
from django.contrib import messages
from gestion.services.vehiculo_service import VehiculoService

service = VehiculoService()


def listar_vehiculos(request):
    vehiculos = service.listar_vehiculos()
    return render(request, 'gestion/vehiculos/listar.html', {'vehiculos': vehiculos})


def crear_vehiculo(request):
    if request.method == 'POST':
        try:
            # Recolectamos datos del formulario
            service.crear_vehiculo(
                patente=request.POST['patente'],
                modelo=request.POST['modelo'],
                color=request.POST['color'],
                precio=request.POST['precio'],
                # 'marca' y 'estado' son los 'name' de los <select> en el HTML
                marca_nombre=request.POST['marca'],
                estado_id=request.POST['estado']
            )
            messages.success(request, "Vehículo creado exitosamente.")
            return redirect('listar_vehiculos')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            # Capturamos errores inesperados de base de datos
            messages.error(request, f"Error del sistema: {str(e)}")

    # GET: Si entramos por primera vez o hubo error, cargamos los combos
    # El método 'obtener_opciones_formulario' nos trae las Marcas y Estados
    contexto = service.obtener_opciones_formulario()
    return render(request, 'gestion/vehiculos/crear.html', contexto)


def borrar_vehiculo(request, patente):
    service.eliminar_vehiculo(patente)
    messages.success(request, "Vehículo eliminado.")
    return redirect('listar_vehiculos')