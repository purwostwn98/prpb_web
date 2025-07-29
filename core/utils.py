from master.models import Truck


def get_truck_by_id(truck_id):
    """
    Helper function to retrieve a Truck object by its ID.
    Returns None if the truck is not found.
    """
    try:
        truck = Truck.objects.get(pk=truck_id)
        return truck
    except Truck.DoesNotExist:
        return None
    
def get_last_maintenance_record(truck_id):
    """
    Helper function to retrieve the last maintenance record for a given truck ID.
    Returns None if no records are found.
    """
    from maintenance.models import Record as MaintenanceRecord
    try:
        last_record = MaintenanceRecord.objects.filter(truck__id=truck_id).order_by('-service_date').first()
        return last_record
    except MaintenanceRecord.DoesNotExist:
        return None
    
def get_second_last_maintenance_record(truck_id, index):
    from maintenance.models import Record as MaintenanceRecord
    try:    
        records = MaintenanceRecord.objects.filter(truck__id=truck_id).order_by('-service_date')
        if len(records) >= 2:
            second_last_record = records[index]
            return second_last_record
        else:
            return None
    except MaintenanceRecord.DoesNotExist:
        return None
    
def get_rolling_avg_3(truck_id):
    from maintenance.models import Record as MaintenanceRecord
    try:
        three_records = MaintenanceRecord.objects.filter(truck__id=truck_id).order_by('-service_date')[:6]
        list_ttf = []
        list_days = []
        for i in range(len(three_records) - 1):
            current_record = three_records[i]
            next_record = three_records[i + 1]
            if current_record.odometer_reading > 0 and next_record.odometer_reading > 0:
                ttf = current_record.odometer_reading - next_record.odometer_reading
                days = (current_record.service_date - next_record.service_date).days
                list_ttf.append(ttf)
                list_days.append(days)
        ttf_average = sum(list_ttf) / len(list_ttf) if len(list_ttf) > 0 else 0
        days_average = sum(list_days) / len(list_days) if len(list_days) > 0 else 0
        return {
            'ttf_average': ttf_average,
            'days_average': days_average
        }
    except MaintenanceRecord.DoesNotExist:
        return None
    
    
