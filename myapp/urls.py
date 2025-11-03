from django.urls import path
from . import views

urlpatterns = [
    path('', views.map, name='map'),
    path('about/', views.about, name='about'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('terminal/', views.terminal, name='terminal'),

    # New API endpoint that returns JSON instead of HTML
    path('api/items/', views.api_items, name='api_items'),

    # New API endpoint for creating items
    path('api/items/create/', views.api_create_item, name='api_create_item'),

    # New API endpoint for updating items
    path('api/items/<int:item_id>/update/', views.api_update_item, name='api_update_item'),
    
    # New API endpoint for deleting items
    path('api/items/<int:item_id>/delete/', views.api_delete_item, name='api_delete_item'),


]
