from django.urls import path
from . import views

urlpatterns = [

    # --- CORE VIEWS (HTML) ---
    path('', views.home, name='home'),
    path('map/', views.map, name='map'),
    path('about/', views.about, name='about'),
    path('terminal/', views.terminal, name='terminal'),

    # --- AUTHENTICATION VIEWS (New) ---
    # Path for custom user registration view
    path('register/', views.register_view, name='register'),

    # --- ITEM API ENDPOINTS ---
    path('api/items/', views.api_items, name='api_items'),
    path('api/items/create/', views.api_create_item, name='api_create_item'),
    path('api/items/<int:item_id>/update/', views.api_update_item, name='api_update_item'),
    path('api/items/<int:item_id>/delete/', views.api_delete_item, name='api_delete_item'),

    # --- ITEM & SENSOR MANAGEMENT VIEWS (HTML) ---
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
   # Sensor editing
    path('sensor/<int:sensor_id>/edit/', views.edit_sensor, name='edit_sensor'),

    # Sensor API endpoints
    path('api/items/<int:item_id>/sensors/', views.api_sensors, name='api_sensors'),
    path('api/items/<int:item_id>/sensors/create/', views.api_create_sensor, name='api_create_sensor'),
    path('api/sensors/<int:sensor_id>/update/', views.api_update_sensor, name='api_update_sensor'),
    path('api/sensors/<int:sensor_id>/delete/', views.api_delete_sensor, name='api_delete_sensor'),



]
