from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('list-merek', views.merek_list, name='merek_list'),
    path('list-truck', views.truck_list, name='truck_list'),
    path('list-company', views.company_list, name='company_list'),
    path('list-vendor', views.vendor_list, name='vendor_list'),
    path('list-part', views.part_list, name='part_list'),
    path('coba-template', views.coba_template, name='coba_template'),
    
    path('form-merek', views.create_Merek, name='create_Merek'),
    path('form-truck', views.create_Truck, name='create_Truck'),
    path('form-company', views.create_Company, name='create_Company'),
    path('form-vendor', views.create_Vendor, name='create_Vendor'),
    path('form-part', views.create_Part, name='create_Part'),

    path('update-merek/<int:pk>/', views.update_Merek, name='update_Merek'),
    path('update-truck/<int:pk>/', views.update_Truck, name='update_Truck'),
    path('update-company/<int:pk>/', views.update_Company, name='update_Company'),
    path('update-vendor/<int:pk>/', views.update_Vendor, name='update_Vendor'),
    path('update-part/<int:pk>/', views.update_Part, name='update_Part'),

    path('delete-merek/<int:pk>/', views.delete_Merek, name='delete_Merek'),
    path('delete-truck/<int:pk>/', views.delete_Truck, name='delete_Truck'),
    path('delete-company/<int:pk>/', views.delete_Company, name='delete_Company'),
    path('delete-vendor/<int:pk>/', views.delete_Vendor, name='delete_Vendor'),
    path('delete-part/<int:pk>/', views.delete_Part, name='delete_Part'),
]
#path('create-form', views.create_form, name='create_form'),