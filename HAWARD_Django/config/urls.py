from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Aquí van las rutas de tu inventario o tienda
    path("", include("inventario.urls")), # o como tengas mapeadas tus vistas
]

# ESTO ES LO QUE FALTA: Añade estas dos líneas al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # O si tus estáticos están sueltos en una carpeta 'static' en la raíz:
    # urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))