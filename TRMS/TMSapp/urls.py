from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import (CompanyCreationView, DriverRegistrationView,
                    TMSAdministratorCreateView)

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('tms_admin_dashboard/', views.tms_admin_dashboard, name='tms_admin_dashboard'),
    path('add_tms_admin/', TMSAdministratorCreateView.as_view(), name='add_tms_admin'),
    path('add_company/', CompanyCreationView.as_view(), name='add_company'),
    path('add_driver/', DriverRegistrationView.as_view(), name='add_driver'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),
<<<<<<< HEAD
    path('compose/', views.compose_message, name='compose_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('messages/', views.messages_view, name='messages'),
    # Add other paths as needed
]
=======
    path('driver/', views.driver, name='driver'),
    path('compose_message/', compose_message, name='compose_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('profile/', views.profile, name='profile'),
    path('tasks/', tasks_view, name='tasks'),
    path('messages/', messages_view, name='messages'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('best-route/', views.display_best_route, name='display_best_route'),
]  

>>>>>>> 6a5e43fc539af7fb733a47b8464b06852430b205
