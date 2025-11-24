from gestion.repositories.reporte_repository import ReporteRepository
from gestion.models.cliente import Cliente

class ReporteService:
    def __init__(self):
        self.repo = ReporteRepository()

    def obtener_reporte_cliente(self, dni):
        """
        Obtiene el historial de alquileres de un cliente, validando su existencia.
        """
        # 1. Validar que el cliente exista
        try:
            cliente = Cliente.objects.get(pk=dni)
        except Cliente.DoesNotExist:
            raise ValueError(f"El cliente con DNI {dni} no existe.")

        # 2. Obtener datos crudos del repositorio
        historial = self.repo.obtener_historial_por_cliente(dni)

        # 3. Calcular Estadísticas (Valor Agregado)
        total_gastado = sum([a.monto_total for a in historial])
        cantidad = len(historial)

        # 4. Formatear la respuesta (DTO)
        detalle_alquileres = []
        for a in historial:
            detalle_alquileres.append({
                "id_alquiler": a.id,
                "vehiculo": f"{a.patente_vehiculo.nombre_marca.nombre} {a.patente_vehiculo.modelo}",
                "patente": a.patente_vehiculo.patente,
                "fecha_inicio": a.fecha_inicio,
                "fecha_fin": a.fecha_fin,
                "monto_total": float(a.monto_total),
                "estado": a.id_estado.nombre
            })

        return {
            "cliente": {
                "nombre": f"{cliente.nombre} {cliente.apellido}",
                "dni": cliente.dni
            },
            "estadisticas": {
                "cantidad_alquileres": cantidad,
                "total_invertido": float(total_gastado)
            },
            "historial": detalle_alquileres
        }

    def ranking_vehiculos(self, top=5):
        """
        Devuelve el top de vehículos más alquilados.
        :param top: Cantidad de vehículos a mostrar (por defecto 5)
        """
        # Llamamos al repositorio que ya tiene la magia del 'annotate' y 'Count'
        ranking_bruto = self.repo.obtener_ranking_vehiculos(top)

        # Formateamos para que el JSON sea más bonito y plano
        resultado = []
        for item in ranking_bruto:
            # item es un dict porque usamos .values() en el repositorio
            resultado.append({
                "patente": item['patente_vehiculo__patente'],
                "modelo": item['patente_vehiculo__modelo'],
                "marca": item['patente_vehiculo__nombre_marca__nombre'],
                "cantidad_alquileres": item['cantidad_alquileres']
            })

        return resultado

    def alquileres_periodo(self, fecha_desde_str, fecha_hasta_str):
        """
        Devuelve los alquileres iniciados en un rango de fechas.
        """
        try:
            f_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
            f_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use AAAA-MM-DD")

        if f_desde > f_hasta:
            raise ValueError("La fecha desde no puede ser mayor a la fecha hasta.")

        raw_data = self.repo.obtener_alquileres_por_periodo(f_desde, f_hasta)

        # Formateamos
        reporte = []
        for a in raw_data:
            reporte.append({
                "id": a.id,
                "fecha_inicio": a.fecha_inicio,
                "fecha_fin": a.fecha_fin,
                "cliente": f"{a.dni_cliente.nombre} {a.dni_cliente.apellido}",
                "vehiculo": f"{a.patente_vehiculo.modelo} ({a.patente_vehiculo.patente})",
                "monto_total": float(a.monto_total),
                "estado": a.id_estado.nombre
            })
        return reporte

    def facturacion_mensual(self, anio_str):
        """
        Devuelve la facturación agrupada por mes para un gráfico de barras.
        Rellena con 0 los meses sin ventas para que el gráfico quede completo (1-12).
        """
        try:
            anio = int(anio_str)
        except ValueError:
            raise ValueError("El año debe ser un número (Ej: 2023).")

        datos_bd = self.repo.obtener_facturacion_mensual(anio)

        # Convertimos el QuerySet a un diccionario para acceso rápido {mes: total}
        mapa_facturacion = {d['mes']: float(d['total_facturado']) for d in datos_bd}

        # Generamos la lista completa de 12 meses (para que el gráfico no tenga huecos)
        reporte_completo = []
        nombres_meses = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        for mes_num in range(1, 13):
            total = mapa_facturacion.get(mes_num, 0.0)
            reporte_completo.append({
                "mes_numero": mes_num,
                "mes_nombre": nombres_meses[mes_num],
                "total_facturado": total
            })

        return {
            "anio": anio,
            "total_anual": sum([x['total_facturado'] for x in reporte_completo]),
            "detalle_mensual": reporte_completo
        }