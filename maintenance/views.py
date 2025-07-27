
from itertools import count
from django.shortcuts import render # type: ignore
from django.http import JsonResponse # type: ignore

from master.models import Truck
from maintenance.models import Record as MaintenanceRecord
from django.db.models import Count # type: ignore

import numpy as np # type: ignore
from reliability.Fitters import Fit_Everything # type: ignore

def dashboard(request):
    """
    View function to render the dashboard page.
    """
    truck_count = Truck.objects.count() 
    trucks = Truck.objects.all().order_by('-year')
    context = { 'trucks': trucks, 'truck_count': truck_count, 'page': ['dashboard', 'dashboard'], 'title': 'Dashboard'}
    return render(request, 'maintenance/dashboard.html', context)


def dashboard_truck(request):
    """
    View function to render the dashboard page.
    """
    truck_id = request.GET.get('id')
    truck_data = Truck.objects.filter(id=truck_id).first()
    oee_value = None
    if truck_data:
        ## menghitung last performance
        maintenance_record = MaintenanceRecord.objects.filter(truck=truck_data).order_by('-odometer_reading').first()
        second_max_record = MaintenanceRecord.objects.filter(truck=truck_data).order_by('-odometer_reading')[1:2].first()
        while maintenance_record.odometer_reading == second_max_record.odometer_reading:
            second_max_record = MaintenanceRecord.objects.filter(truck=truck_data).order_by('-odometer_reading')[1:3].first()
        max_record = maintenance_record.odometer_reading if maintenance_record else 0
        second_max_record = second_max_record.odometer_reading if second_max_record else 0
        # print(max_record)
        # print(second_max_record)
        # print(max_record - second_max_record)
        ideal_odometer = 10000
        availability = (max_record - second_max_record) / ideal_odometer * 100 if maintenance_record and second_max_record else 0
        performance = ((max_record - second_max_record) / ideal_odometer) * 100 if maintenance_record else 0
        quality = 100  # Assuming quality is always 100% for this example
        oee_value = (availability * performance * quality) / 10000 if availability and performance else 0
        if oee_value > 100:
            oee_value = 99.99

        ## menghitung mttf
        mttf = 0
        pembagi = 0

        ## Reliablity
        jumlah_gagal = 0
        pembagi_reliability = 0
        maintenance_records = MaintenanceRecord.objects.filter(truck=truck_data, odometer_reading__gt=0).order_by('odometer_reading')
        array_ttf = []
        for i in range(len(maintenance_records) - 1):
            current_record = maintenance_records[i]
            next_record = maintenance_records[i + 1]
            # print(current_record.odometer_reading)
            # print(next_record.odometer_reading)
            # print("=====")
            if current_record.odometer_reading > 0 and next_record.odometer_reading > 0:
                # MTTF
                if (next_record.odometer_reading - current_record.odometer_reading) > 1000:
                    ttf = next_record.odometer_reading - current_record.odometer_reading
                    if ttf < 15000:
                        ttf = ttf
                    else:
                        ttf = 15000
                    array_ttf.append(next_record.odometer_reading - current_record.odometer_reading)
                    mttf += (next_record.odometer_reading - current_record.odometer_reading)
                    pembagi += 1
                # Reliability
                if (next_record.odometer_reading - current_record.odometer_reading) > 1000:
                    pembagi_reliability += 1
                    if (next_record.odometer_reading - current_record.odometer_reading) < 8000:
                        jumlah_gagal += 1
        # print(array_ttf)
        # results = Fit_Everything(failures=array_ttf, print_results=True)
        # best_dist = results.best_distribution
        # print(f"MTTF for the best-fit distribution ({best_dist.name}): {best_dist.mean:.2f} hours")

        ## Hitung MTTF
        if pembagi > 0:
            mttf = mttf / pembagi
        else:
            mttf = 0
        # persentase mttf
        persentase_mttf = mttf / ideal_odometer * 100 if mttf else 0

        ## Hitung Reliability
        reliability = (pembagi_reliability - jumlah_gagal) / pembagi_reliability * 100 if pembagi_reliability > 0 else 0

    context = {
        'page': ['dashboard', 'dashboard'], 'title': 'Dashboard Truck',
        'truck_data': truck_data,
        'oee_value': round(oee_value,2),
        'mttf': round(mttf,2),
        'jumlah_maintenance': len(maintenance_records),
        'persentase_mttf': round(persentase_mttf,2),
        'reliability': round(reliability,2),
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

def getMttfValue(request, id):
    """
    View function to get the MTTF value for a specific truck.
    """
    truck_id = id
    truck_data = Truck.objects.filter(id=truck_id).first()
    mttf = 0
    array_ttf = []
    labels = []
    if truck_data:
        maintenance_records = MaintenanceRecord.objects.filter(truck=truck_data, odometer_reading__gt=0).order_by('odometer_reading')
        for i in range(len(maintenance_records) - 1):
            current_record = maintenance_records[i]
            next_record = maintenance_records[i + 1]
            if current_record.odometer_reading > 0 and next_record.odometer_reading > 0:
                if (next_record.odometer_reading - current_record.odometer_reading) > 1000:
                    ttf = next_record.odometer_reading - current_record.odometer_reading
                    array_ttf.append(ttf)  
                    labels.append("Service " + str(i+1) + " - " + str(i+2))
        #  Fit the distribution to the data
        results = Fit_Everything(failures=array_ttf, print_results=True)
        best_dist = results.best_distribution  
        mttf = best_dist.mean if best_dist else 0
        # print(f"MTTF for the best-fit distribution ({best_dist.name}): {best_dist.mean:.2f} hours")
        distribution_name = best_dist.name if best_dist else "Unknown"

        # Calculate reliability score for the best-fit distribution at a given odometer value (e.g., ideal_odometer)
        ideal_odometer = 10000
        reliability_score = best_dist.SF(ideal_odometer) * 100 if best_dist else 0
        
        # distribution data
        distributin_data = {
            'labels': labels,
            'values': array_ttf,
            'distribution_name': distribution_name,
        }

        print(distributin_data)
    

    return JsonResponse({'mttf': round(mttf,2), 'distribution_name': distribution_name, 'reliability_score': round(reliability_score,2), 'distribution_data': distributin_data})