from django.contrib import admin
from django.urls import include, path
from TMSapp.admin import custom_admin_site 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('TMSapp.urls')),
    path('custom_admin/', custom_admin_site.urls),
]
