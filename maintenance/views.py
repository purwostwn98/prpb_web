

from itertools import count
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore

from master.models import ComponentType, Truck
from delivery.models import Shipping
from maintenance.models import Record as MaintenanceRecord
from maintenance.models import TruckDeviceModel, Log, RecordItem
from maintenance.forms import RecordForm, RecordItemFormSet, TruckDeviceForm
from django.db.models import Count, Max, Q # type: ignore
from django.db.models.functions import TruncMonth # type: ignore
from django.core.paginator import Paginator # type: ignore
from django.db import transaction # type: ignore

from django.utils import timezone
from datetime import datetime, timedelta, date # type: ignore
import numpy as np # type: ignore

from core.utils import *
from maintenance.analytics import (
    NEWEST_FIRST, STATUS_LABELS, STATUS_ORDER, component_due_list, component_records, due_summary, fitted_mttf,
    get_component, get_warning_component, next_service, reliability_summary, tracked_components, warning_components,
)
from master.odometer import odometer_error, record_odometer
from django.contrib import messages # type: ignore
from django.utils.http import url_has_allowed_host_and_scheme # type: ignore
from django.views.decorators.http import require_POST # type: ignore

BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']


def dashboard(request):
    """
    View function to render the dashboard page.
    """
    truck_count = Truck.objects.count()

    status_counts = {
        row['status']: row['count']
        for row in Truck.objects.values('status').annotate(count=Count('id'))
    }
    active_count = status_counts.get('active', 0)
    maintenance_count = status_counts.get('maintenance', 0)
    inactive_count = status_counts.get('inactive', 0)

    # work that is waiting on someone: shipments on the road, maintenance not finished
    running_shipping_count = Shipping.objects.filter(status='on_progress').count()
    open_record_statuses = ['draft', 'requested', 'awaiting_approval', 'approved', 'in_progress']
    open_record_count = MaintenanceRecord.objects.filter(status__in=open_record_statuses).count()

    total_maintenance_count = MaintenanceRecord.objects.count()

    serviced_truck_ids = MaintenanceRecord.objects.values_list('truck_id', flat=True).distinct()
    never_serviced_trucks = Truck.objects.select_related('brand').exclude(id__in=serviced_truck_ids)
    never_serviced_count = never_serviced_trucks.count()

    top_trucks = (
        MaintenanceRecord.objects
        .values('truck__id', 'truck__license_plate', 'truck__model')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    recent_records = (
        MaintenanceRecord.objects
        .select_related('truck', 'vendor')
        .order_by('-service_date', '-id')[:8]
    )

    # early warning summary for the default scheduled component (engine oil)
    warning_component = get_warning_component()
    warning_rows = component_due_list(warning_component) if warning_component else []
    warning_counts = due_summary(warning_rows)
    warning_urgent = [r for r in warning_rows if r['status'] in ('overdue', 'soon')][:5]

    context = {
        'warning_component': warning_component,
        'warning_counts': warning_counts,
        'warning_urgent': warning_urgent,
        'truck_count': truck_count,
        'running_shipping_count': running_shipping_count,
        'open_record_count': open_record_count,
        'open_record_statuses': open_record_statuses,
        'active_count': active_count,
        'maintenance_count': maintenance_count,
        'inactive_count': inactive_count,
        'total_maintenance_count': total_maintenance_count,
        'never_serviced_trucks': never_serviced_trucks,
        'never_serviced_count': never_serviced_count,
        'top_trucks': top_trucks,
        'recent_records': recent_records,
        'page': ['dashboard', 'dashboard'],
        'title': 'Dashboard',
    }
    return render(request, 'maintenance/dashboard.html', context)


def dashboard_truck(request):
    """
    View function to render the dashboard page of one truck.
    Analytics are computed for one component type (?component=CODE, default fuel filter).
    """
    truck_id = request.GET.get('id')
    if not (truck_id and truck_id.isdigit()):
        truck_id = None
    truck_data = Truck.objects.filter(id=truck_id).first() if truck_id else None
    component = get_component(request.GET.get('component'))

    summary = {'oee_value': 0, 'mttf': 0, 'persentase_mttf': 0, 'reliability': 0, 'jumlah_maintenance': 0}
    last_maintenance = None
    if truck_data:
        summary = reliability_summary(truck_data, component)
        last_maintenance = component_records(truck_data.id, component).order_by(*NEWEST_FIRST).first()

    truck_device = TruckDeviceModel.objects.filter(truck=truck_data).order_by('-installed_at').first() if truck_data else None
    warning_component = get_warning_component()
    warning = None
    if truck_data and warning_component:
        warning = component_due_list(warning_component, Truck.objects.filter(pk=truck_data.pk))[0]

    context = {
        'page': ['dashboard', 'dashboard'], 'title': 'Dashboard Truck',
        'warning_component': warning_component,
        'warning': warning,
        'truck_data': truck_data,
        'device_model': truck_device.device_model if truck_device else None,
        'component': component,
        'components': tracked_components(),
        'last_service_odometer': last_maintenance.odometer_reading if last_maintenance else 0,
        **summary,
    }
    return render(request, 'maintenance/dashboard_truck.html', context)

def statisticBrandChart(request):
    """
    View function to render the statistic brand chart page.
    """
    brands = Truck.objects.values('brand__nama').annotate(count=Count('id'))
    data = {
        'labels': [b['brand__nama'] for b in brands],
        'values': [b['count'] for b in brands],
    }   
    return JsonResponse(data)

def maintenanceTrendChart(request):
    """
    View function to return maintenance record volume for the last 6 months
    that actually have data (relative to the data itself, not the server clock,
    since historical data may not extend to the current month).
    """
    qs = (
        MaintenanceRecord.objects
        .exclude(service_date__year__lt=1900)
        .annotate(month=TruncMonth('service_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')[:6]
    )
    rows = list(qs)[::-1]
    labels = [f"{BULAN[row['month'].month - 1]} {row['month'].year}" for row in rows]
    note = None
    last_date = MaintenanceRecord.objects.exclude(service_date__year__lt=1900).aggregate(d=Max('service_date'))['d']
    if rows and last_date:
        next_month = (last_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        if last_date < next_month - timedelta(days=1) and last_date.replace(day=1) == rows[-1]['month'].replace(day=1):
            # the last month only has a few days of data; mark it so the drop is not misread
            labels[-1] += '*'
            note = f"* Data bulan terakhir hanya sampai {last_date.day} {BULAN[last_date.month - 1]} {last_date.year}."
    data = {
        'labels': labels,
        'values': [row['count'] for row in rows],
        'note': note,
    }
    return JsonResponse(data)

def maintenanceTypeChart(request):
    """
    View function to return the distribution of maintenance records by type.
    """
    type_labels = dict(MaintenanceRecord.MAINTENANCE_TYPE_CHOICES)
    qs = MaintenanceRecord.objects.values('maintenance_type').annotate(count=Count('id')).order_by('-count')
    labels = []
    values = []
    for row in qs:
        key = row['maintenance_type']
        label = type_labels.get(key, key.title()) if key else 'Tidak diketahui'
        labels.append(label)
        values.append(row['count'])
    return JsonResponse({'labels': labels, 'values': values})

def getMttfValue(request, id):
    """
    View function to get the fitted MTTF value of one component for a specific truck.
    """
    component = get_component(request.GET.get('component'))
    result = fitted_mttf(id, component)
    distributin_data = {
        'labels': result['labels'],
        'values': result['values'],
        'distribution_name': result['distribution_name'],
    }
    return JsonResponse({
        'mttf': round(result['mttf'], 2),
        'distribution_name': result['distribution_name'],
        'reliability_score': round(result['reliability_score'], 2),
        'distribution_data': distributin_data,
    })

def getInputDataML(request, id):
    """
    View function to get the replacement statistics and the predicted next service
    of one component for a specific truck.
    """
    truck_data = get_object_or_404(Truck, id=id)
    component = get_component(request.GET.get('component'))
    result = next_service(truck_data, component, default_truck_age=1)
    if result is None:
        return JsonResponse({'error': 'Belum ada riwayat penggantian komponen ini.'}, status=404)
    return JsonResponse(result)

def getFuelFilterPressure(request, id):
    """
    View function to get the fuel filter pressure for a specific truck.
    """
    truck_id = id
    # get truck device_id
    truckDevice = TruckDeviceModel.objects.filter(truck__id=truck_id).first()
    if not truckDevice:
        return JsonResponse({'error': 'Truck device not found'}, status=404)
    device_id = truckDevice.device_model
    latest_reading = get_fuel_filter_pressure_from_api(device_id)
    if not latest_reading:
        return JsonResponse({'error': 'Fuel filter pressure data unavailable'}, status=502)

    first_pressure_value = abs(float(latest_reading['pressure_value']))
    timestamp_values = latest_reading['timestamp']

    # convert timestamp to readable format
    dt = datetime.fromisoformat(timestamp_values.replace('Z', '+00:00'))
    local_dt = timezone.localtime(dt)
    readable = local_dt.strftime('%B %d, %Y at %I:%M:%S %p')

    response = {
        'datetime': readable,
        'pressure_values': first_pressure_value,
    }
    return JsonResponse(response)

def getMaintenanceHistory(request, id):
    """
    View function to get the maintenance history of one component for a specific truck.
    """
    component = get_component(request.GET.get('component'))
    maintenance_records = (
        component_records(id, component)
        .select_related('vendor')
        .prefetch_related('items__component_type')
        .order_by(*NEWEST_FIRST)[:8]
    )
    status_row_class = {
        'done': 'table-success',
        'completed': 'table-success',
        'approved': 'table-success',
        'cancelled': 'table-danger',
        'rejected': 'table-danger',
        'draft': 'table-secondary',
    }
    history = []
    for record in maintenance_records:
        history.append({
            'date': record.service_date.strftime('%Y-%m-%d'),
            'odometer': record.odometer_reading,
            'service': record.get_maintenance_type_display() or 'Tidak diketahui',
            'components': ', '.join(
                f"{item.get_action_display()} {item.component_type.name}" for item in record.items.all()
            ),
            'vendor': record.vendor.name if record.vendor else '-',
            'cost': float(record.cost) if record.cost else 0,
            'status': record.get_status_display(),
            'row_class': status_row_class.get(record.status, 'table-warning'),
        })
    return JsonResponse({'history': history})

# Early warning penggantian komponen (mis. ganti oli)

def early_warning(request):
    """
    Trucks that are (almost) due for replacing a component, with the remaining KM/days.
    """
    component = get_warning_component(request.GET.get('component'))
    rows = component_due_list(component) if component else []
    counts = due_summary(rows)

    status_filter = request.GET.get('status')
    search = request.GET.get('q', '').strip()
    if status_filter in STATUS_LABELS:
        rows = [r for r in rows if r['status'] == status_filter]
    if search:
        rows = [r for r in rows if search.lower() in r['truck'].license_plate.lower()]

    context = {
        'component': component,
        'components': warning_components(),
        'rows': rows,
        'counts': counts,
        'status_cards': [(status, STATUS_LABELS[status], counts.get(status, 0)) for status in STATUS_ORDER],
        'status_filter': status_filter,
        'search': search,
        'page': ['maintenance', 'early_warning'],
        'title': 'Early Warning Penggantian',
    }
    return render(request, 'maintenance/early_warning.html', context)


@require_POST
def update_odometer(request, truck_id):
    """
    Manual odometer input by an admin (e.g. from the early warning page).
    """
    truck = get_object_or_404(Truck, pk=truck_id)
    raw = request.POST.get('odometer', '').replace('.', '').replace(',', '').strip()
    if not raw.isdigit():
        messages.error(request, 'KM harus berupa angka.')
    else:
        reading = int(raw)
        error = odometer_error(truck, reading)
        if error:
            messages.error(request, error)
        else:
            record_odometer(truck, reading, 'manual')
            messages.success(request, f"KM truck {truck.license_plate} diperbarui menjadi {reading:,}.".replace(',', '.'))
    next_url = request.POST.get('next')
    if not next_url or not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = 'early_warning'
    return redirect(next_url)


# Manajemen Maintenance Truck (Record)

def fill_cost_from_items(form_record, record):
    """When the cost was left empty, use the total of the component prices."""
    if getattr(form_record, 'cost_from_items', False):
        record.cost = sum(item.subtotal for item in record.items.all())
        record.save(update_fields=['cost'])


def record_list(request):
    """
    View function to list all maintenance records.
    Server-side paginated and filterable: with 5,600+ records, dumping
    everything into one client-side DataTable would not scale.
    """
    records = (
        MaintenanceRecord.objects.select_related('truck', 'vendor')
        .prefetch_related('items__component_type')
        .order_by('-service_date', '-id')
    )

    search = request.GET.get('q', '').strip()
    if search:
        records = records.filter(
            Q(order_reference__icontains=search) |
            Q(truck__license_plate__icontains=search) |
            Q(technician_name__icontains=search)
        )

    status_filter = request.GET.getlist('status')
    if status_filter:
        records = records.filter(status__in=status_filter)

    component_filter = request.GET.get('component', '')
    if component_filter:
        records = records.filter(
            pk__in=RecordItem.objects.filter(component_type__code=component_filter).values('record_id')
        )

    paginator = Paginator(records, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    total_count = MaintenanceRecord.objects.count()
    done_count = MaintenanceRecord.objects.filter(status__in=['done', 'completed', 'approved']).count()
    pending_count = MaintenanceRecord.objects.filter(
        status__in=['draft', 'requested', 'awaiting_approval', 'in_progress']
    ).count()

    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'done_count': done_count,
        'pending_count': pending_count,
        'search': search,
        'status_filter': status_filter,
        'status_choices': MaintenanceRecord.STATUS_TYPE_CHOICES,
        'component_filter': component_filter,
        'component_choices': ComponentType.objects.order_by('name'),
        'page': ['maintenance', 'record'],
        'title': 'Daftar Maintenance',
    }
    return render(request, 'maintenance/record_list.html', context)


def record_detail(request, pk):
    """
    View function to show the detail of a maintenance record: info, components worked on, and log history.
    """
    record = get_object_or_404(MaintenanceRecord.objects.select_related('truck', 'vendor'), pk=pk)
    items = RecordItem.objects.filter(record=record).select_related('component_type', 'part')
    logs = Log.objects.filter(record=record).order_by('-log_date')
    context = {
        'record': record,
        'items': items,
        'logs': logs,
        'page': ['maintenance', 'record'],
        'title': 'Detail Maintenance',
    }
    return render(request, 'maintenance/record_detail.html', context)


def create_Record(request):
    """
    View function to create a new maintenance record together with the components worked on.
    """
    context = {'page': ['maintenance', 'record'], 'title': 'Tambah Maintenance'}
    item_initial = []
    record_initial = {}
    if request.method == 'GET':
        # prefilled from the early warning page: ?truck=ID&component=CODE
        truck = Truck.objects.filter(pk=request.GET.get('truck')).first() if request.GET.get('truck', '').isdigit() else None
        today = timezone.localdate()
        record_initial = {'booking_date': today, 'service_date': today}
        if truck:
            record_initial.update({
                'truck': truck, 'maintenance_type': 'preventive',
                'odometer_reading': truck.current_odometer, 'status': 'done',
            })
        component = ComponentType.objects.filter(code=request.GET.get('component')).first()
        if component:
            item_initial = [{'component_type': component, 'action': RecordItem.ACTION_REPLACE}]
    form_record = RecordForm(request.POST or None, initial=record_initial)
    formset = RecordItemFormSet(
        request.POST or None, instance=MaintenanceRecord(), prefix='items', initial=item_initial,
    )
    if request.method == 'POST':
        if form_record.is_valid() and formset.is_valid():
            with transaction.atomic():
                record = form_record.save(commit=False)
                record.input_by = request.user.id if request.user.is_authenticated else None
                record.save()
                formset.instance = record
                formset.save()
                fill_cost_from_items(form_record, record)
                Log.objects.create(
                    record=record,
                    log_type=record.status,
                    log_description=f"Record {record.order_reference} dibuat dengan status {record.get_status_display()}.",
                    updated_by=request.user.id if request.user.is_authenticated else 0,
                )
            return redirect('record_list')
    context['form_record'] = form_record
    context['formset'] = formset
    context['component_units'] = {c.pk: c.unit for c in ComponentType.objects.all()}
    return render(request, 'maintenance/create_record.html', context)


def update_Record(request, pk):
    """
    View function to update an existing maintenance record and its components.
    """
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    old_status = record.status
    form_record = RecordForm(request.POST or None, instance=record)
    formset = RecordItemFormSet(request.POST or None, instance=record, prefix='items')
    if request.method == 'POST':
        if form_record.is_valid() and formset.is_valid():
            with transaction.atomic():
                updated_record = form_record.save()
                formset.save()
                fill_cost_from_items(form_record, updated_record)
                if old_status != updated_record.status:
                    Log.objects.create(
                        record=updated_record,
                        log_type=updated_record.status,
                        log_description=f"Status berubah dari {old_status} menjadi {updated_record.get_status_display()}.",
                        updated_by=request.user.id if request.user.is_authenticated else 0,
                    )
                else:
                    Log.objects.create(
                        record=updated_record,
                        log_type=updated_record.status,
                        log_description=f"Record {updated_record.order_reference} diperbarui.",
                        updated_by=request.user.id if request.user.is_authenticated else 0,
                    )
            return redirect('record_list')
    context = {
        'form_record': form_record,
        'formset': formset,
        'component_units': {c.pk: c.unit for c in ComponentType.objects.all()},
        'page_title': 'Update Maintenance',
        'page': ['maintenance', 'record'],
        'title': 'Update Maintenance',
    }
    return render(request, 'maintenance/create_record.html', context)


def delete_Record(request, pk):
    """
    View function to delete a maintenance record.
    """
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
    return redirect('record_list')


# Manajemen Perangkat IoT / Device Truck

def device_list(request):
    """
    View function to list all truck IoT devices.
    """
    devices = TruckDeviceModel.objects.select_related('truck', 'truck__brand').order_by('-installed_at')
    total_trucks = Truck.objects.count()
    trucks_with_device = devices.values('truck_id').distinct().count()
    trucks_without_device = total_trucks - trucks_with_device
    context = {
        'devices': devices,
        'total_trucks': total_trucks,
        'trucks_with_device': trucks_with_device,
        'trucks_without_device': trucks_without_device,
        'page': ['maintenance', 'device'],
        'title': 'Daftar Device Truck',
    }
    return render(request, 'maintenance/device_list.html', context)


def create_Device(request):
    """
    View function to assign a new IoT device to a truck.
    """
    context = {'page': ['maintenance', 'device'], 'title': 'Tambah Device Truck'}
    form_device = TruckDeviceForm(request.POST or None)
    if request.method == 'POST':
        if form_device.is_valid():
            form_device.save()
            return redirect('device_list')
    context['form_device'] = form_device
    return render(request, 'maintenance/create_device.html', context)


def update_Device(request, pk):
    """
    View function to update an existing truck IoT device.
    """
    device = get_object_or_404(TruckDeviceModel, pk=pk)
    form_device = TruckDeviceForm(request.POST or None, instance=device)
    if request.method == 'POST':
        if form_device.is_valid():
            form_device.save()
        return redirect('device_list')
    context = {
        'form_device': form_device,
        'page_title': 'Update Device Truck',
        'page': ['maintenance', 'device'],
        'title': 'Update Device Truck',
    }
    return render(request, 'maintenance/create_device.html', context)


def delete_Device(request, pk):
    """
    View function to remove a truck IoT device.
    """
    device = get_object_or_404(TruckDeviceModel, pk=pk)
    if request.method == 'POST':
        device.delete()
    return redirect('device_list')