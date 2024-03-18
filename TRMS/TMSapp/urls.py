from django.urls import path
from . import views
from .views import compose_message, inbox
from .views import tasks_view, messages_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
      
    #path('login/', auth_views.LoginView.as_view(), name='login'),  # Ensure this is correctly configured
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # path('', auth_views.LoginView.as_view(), name='login'),
    path('tms_admin_dashboard/', views.tms_admin_dashboard, name='tms_admin_dashboard'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/', views.driver, name='driver'),
    path('compose_message/', compose_message, name='compose_message'),
    path('inbox/', inbox, name='inbox'),
    path('tasks/', tasks_view, name='tasks'),
    path('messages/', messages_view, name='messages'),
]
