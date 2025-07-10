from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard-truck', views.dashboard_truck, name='dashboard-truck'),
    path('dinamis/statistic-brand-chart/', views.statisticBrandChart, name='statistic-brand-chart'),
    path('dinamis/get_mttf/<int:id>/', views.getMttfValue, name='get_mttf'),
]