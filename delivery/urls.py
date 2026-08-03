from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('list-shipping', views.shipping_list, name='shipping_list'),
    path('shipping/<int:pk>/', views.shipping_detail, name='shipping_detail'),
    path('form-shipping', views.create_Shipping, name='create_Shipping'),
    path('update-shipping/<int:pk>/', views.update_Shipping, name='update_Shipping'),
    path('delete-shipping/<int:pk>/', views.delete_Shipping, name='delete_Shipping'),
]
