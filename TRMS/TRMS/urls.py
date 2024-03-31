from django.contrib import admin
from django.urls import include, path
from TMSapp.admin import custom_admin_site
from django.conf import settings
from django.conf.urls.static import static 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('TMSapp.urls')),
    path('custom_admin/', custom_admin_site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
