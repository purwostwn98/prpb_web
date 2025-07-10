from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('merek', views.merek_list, name='merek_list'),
    path('coba-template', views.coba_template, name='coba_template'),
]
