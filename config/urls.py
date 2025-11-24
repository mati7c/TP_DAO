from django.contrib import admin
from django.urls import path, include  # <--- No olvides importar include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Esta línea conecta el cerebro principal con tu archivo de la app
    # Si no está esta línea, nada de lo que escribas en gestion/urls.py funcionará
    path('', include('gestion.urls')),
]

