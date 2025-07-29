from master.models import Truck
import requests # type:ignore
import json
import numpy as np



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
        ttf_std = np.std(list_ttf) if len(list_ttf) > 0 else 0
        days_average = sum(list_days) / len(list_days) if len(list_days) > 0 else 0
        days_std = np.std(list_days) if len(list_days) > 0 else 0
        return {
            'ttf_average': ttf_average,
            'days_average': days_average,
            'ttf_std': ttf_std,
            'days_std': days_std,
        }
    except MaintenanceRecord.DoesNotExist:
        return None
    
def get_commulative_service(truck_id):
    from maintenance.models import Record as MaintenanceRecord
    try:
        #count all service
        total_service = MaintenanceRecord.objects.filter(truck__id=truck_id).count()
        return total_service
    except MaintenanceRecord.DoesNotExist:
        return None

def get_commulative_km_average(truck_id):
    from maintenance.models import Record as MaintenanceRecord
    try:
        records = MaintenanceRecord.objects.filter(truck__id=truck_id).order_by('service_date')
        total_km = 0
        num_intervals = 0
        for i in range(len(records) - 1):
            current_record = records[i]
            next_record = records[i + 1]
            km_diff = next_record.odometer_reading - current_record.odometer_reading
            total_km += km_diff
            num_intervals += 1
        
        if num_intervals > 0:
            return total_km / num_intervals 
        else:
            return 0
    except MaintenanceRecord.DoesNotExist:
        return None


def get_commulative_days_average(truck_id):
    from maintenance.models import Record as MaintenanceRecord
    try:
        records = MaintenanceRecord.objects.filter(truck__id=truck_id).order_by('service_date')
        total_days = 0
        num_intervals = 0
        for i in range(len(records) - 1):
            current_record = records[i]
            next_record = records[i + 1]
            days_diff = (next_record.service_date - current_record.service_date).days
            total_days += days_diff
            num_intervals += 1
        
        if num_intervals > 0:
            return total_days / num_intervals
        else:
            return 0
    except MaintenanceRecord.DoesNotExist:
        return None

def get_prediction_from_api(payload_data):
    """
    Sends data to the prediction API and returns the result.
    
    Args:
        payload_data (dict): A dictionary containing the features for the prediction model.
        
    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    url = "https://sofipremas2.ums.ac.id/predict"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        # Using requests.post is a more direct way to make a POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload_data), timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        # In a real application, you would want to log this error
        print(f"An error occurred while calling the prediction API: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response from API. Response text: {response.text}")
        return None
    
