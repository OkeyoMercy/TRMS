from django.urls import path
from . import views
from .views import compose_message, inbox, route_view
from .views import tasks_view, messages_view
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (company_creation_view, compose_message, dashboard_redirect,
                    display_best_route, driver_dashboard,
                    driver_registration_view, inbox, login_view,
                    manager_dashboard, messages_view, profile, send_message,
                    tasks_view, tms_admin_dashboard,
                    tms_adminstrator_create_view)

urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('add_driver/', driver_registration_view, name='add_driver'),
    path('add_company/', company_creation_view, name='add_company'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('tms_admin_dashboard/', tms_admin_dashboard, name='tms_admin_dashboard'),
    path('add_tms_admin/', tms_adminstrator_create_view, name='add_tms_admin'),
    path('manager_dashboard/', manager_dashboard, name='manager_dashboard'),
    path('driver_dashboard/', driver_dashboard, name='driver_dashboard'),
    path('compose/', compose_message, name='compose_message'),
    path('inbox/', inbox, name='inbox'),
    path('tasks/', tasks_view, name='tasks'),
    path('messages/', messages_view, name='messages'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('best-route/', views.display_best_route, name='display_best_route'),
    path('tracking/', views.track, name='track'),
    path('find-route/', views.find_best_route, name='find_best_route'),
    path('find_best_route/', views.find_best_route, name='find_best_route'),
    path('update-weather/<int:route_id>/', views.update_weather_for_route, name='update_weather_for_route'),
    path('route/', views.route_view, name='route_view'),
    path('get-route/', views.get_route, name='get_route'),
    path('compose_message/', compose_message, name='compose_message'),
    path('inbox/', inbox, name='inbox'),
    path('profile/', profile, name='profile'),
    path('tasks/', tasks_view, name='tasks'),
    path('messages/', messages_view, name='messages'),
    path('send_message/<int:recipient_id>/', send_message, name='send_message'),
    path('best-route/', display_best_route, name='display_best_route'),
]
