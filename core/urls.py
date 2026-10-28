from django.urls import path
from . import views

urlpatterns = [
    path('list-user', views.user_list, name='user_list'),
    path('form-user', views.create_User, name='create_User'),
    path('update-user/<int:pk>/', views.update_User, name='update_User'),
    path('delete-user/<int:pk>/', views.delete_User, name='delete_User'),
]
