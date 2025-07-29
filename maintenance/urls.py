from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard-truck', views.dashboard_truck, name='dashboard-truck'),
    path('dinamis/statistic-brand-chart/', views.statisticBrandChart, name='statistic-brand-chart'),
    path('dinamis/get_mttf/<int:id>/', views.getMttfValue, name='get_mttf'),
    path('dinamis/get-input-data/<int:id>/', views.getInputDataML, name='get_input_data'),
]