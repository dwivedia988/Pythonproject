from django.urls import path
from . import views
from .views import create_checkout_session

urlpatterns = [
	path('', views.ApiOverview, name='home'),
    path('create/', views.add_items, name='add-items'),
    path('all/', views.view_items, name='view_items'),
    path('update/<int:pk>/', views.update_items, name='update-items'),
    path('item/<int:pk>/delete/', views.delete_items, name='delete-items'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
]

