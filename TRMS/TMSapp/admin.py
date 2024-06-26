from django.contrib import admin
from pyexpat import model
from django.contrib import admin
from .models import Message, Route
from django.contrib import admin
from .models import Driver
from .models import Profile
from .models import Message
from .models import Driver, Message, Profile
admin.site.register(Driver)
from django.contrib.admin import AdminSite, ModelAdmin

admin.site.register(Message)
admin.site.register(Route)
admin.site.register(Profile)
# admin_site.register(Model, ModelAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'timestamp')
    

class CustomAdminSite(AdminSite):
    site_header = "My Custom Admin"
    site_title = "My Custom Admin Portal"
    index_title = "Welcome to the Custom Admin Portal"
custom_admin_site = CustomAdminSite(name='custom_admin')



class ModelAdmin(ModelAdmin):
   
    list_display = ['name']  # Example fields

