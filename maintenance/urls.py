from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard-truck', views.dashboard_truck, name='dashboard-truck'),
    path('dinamis/statistic-brand-chart/', views.statisticBrandChart, name='statistic-brand-chart'),
    path('dinamis/maintenance-trend-chart/', views.maintenanceTrendChart, name='maintenance-trend-chart'),
    path('dinamis/maintenance-type-chart/', views.maintenanceTypeChart, name='maintenance-type-chart'),
    path('dinamis/get_mttf/<int:id>/', views.getMttfValue, name='get_mttf'),
    path('dinamis/get-input-data/<int:id>/', views.getInputDataML, name='get_input_data'),
    path('dinamis/get-fuel-filter-pressure/<int:id>/', views.getFuelFilterPressure, name='get_fuel_filter_pressure'),
    path('dinamis/get-maintenance-history/<int:id>/', views.getMaintenanceHistory, name='get_maintenance_history'),

    path('list-record', views.record_list, name='record_list'),
    path('record/<int:pk>/', views.record_detail, name='record_detail'),
    path('form-record', views.create_Record, name='create_Record'),
    path('update-record/<int:pk>/', views.update_Record, name='update_Record'),
    path('delete-record/<int:pk>/', views.delete_Record, name='delete_Record'),

    path('list-device', views.device_list, name='device_list'),
    path('form-device', views.create_Device, name='create_Device'),
    path('update-device/<int:pk>/', views.update_Device, name='update_Device'),
    path('delete-device/<int:pk>/', views.delete_Device, name='delete_Device'),
]