from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('list-shipping', views.shipping_list, name='shipping_list'),
    path('shipping/<int:pk>/', views.shipping_detail, name='shipping_detail'),
    path('form-shipping', views.create_Shipping, name='create_Shipping'),
    path('update-shipping/<int:pk>/', views.update_Shipping, name='update_Shipping'),
    path('delete-shipping/<int:pk>/', views.delete_Shipping, name='delete_Shipping'),

    path('list-shippingto', views.shippingto_list, name='shippingto_list'),
    path('form-shippingto', views.create_ShippingTo, name='create_ShippingTo'),
    path('update-shippingto/<int:pk>/', views.update_ShippingTo, name='update_ShippingTo'),
    path('delete-shippingto/<int:pk>/', views.delete_ShippingTo, name='delete_ShippingTo'),
]
