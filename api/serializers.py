import datetime
from rest_framework import serializers
from master.models import Merek, Truck
from master.models import Driver
from core.utils import *
from delivery.models import Shipping, ShippingItem, ShippingTo
from maintenance.models import Record as MaintenanceRecord  # Add this import at the module level
from django.contrib.auth import get_user_model

import numpy as np # type: ignore
from reliability.Fitters import Fit_Everything # type: ignore

class MerekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merek
        fields = ['id', 'nama', 'deskripsi', 'created_at', 'updated_at']

class TruckSerializer(serializers.ModelSerializer):
    brand_nama = serializers.SerializerMethodField()

    def get_brand_nama(self, obj):
        return obj.brand.nama if obj.brand else None

    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'brand', 'brand_nama']

class UserDriverSerializer(serializers.ModelSerializer):
    data_driver = serializers.SerializerMethodField()

    def get_data_driver(self, obj):
        user_id = obj.id
        driver = Driver.objects.filter(user_id=user_id).first()
        if driver:
            return {
                'success': True,
                'id_driver': driver.id,
                'license_number': driver.license_number,
                'phone_number': driver.phone_number,
            }
        else:
            return {
                'success': False,
                'message': 'Driver tidak ditemukan untuk user ini.',
            }


    id_user = serializers.SerializerMethodField()
    def get_id_user(self, obj):
        return obj.id

    class Meta:
        model = get_user_model()
        fields = ['id_user', 'username', 'email', 'first_name', 'last_name', 'data_driver']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email']

class ShippingToSerializer(serializers.ModelSerializer):

    spbu_name = serializers.SerializerMethodField()
    def get_spbu_name(self, obj):
        if obj.spbu:
            spbu_name = f"{obj.spbu.name} - {obj.spbu.address}"
        return spbu_name if obj.spbu else None
    
    items = serializers.SerializerMethodField()
    def get_items(self, obj):
        shippingto_id = obj.id
        shipping_items = ShippingItem.objects.filter(shippingto_id=shippingto_id)
        return ShippingItemSerializer(shipping_items, many=True).data

    class Meta:
        model = ShippingTo
        fields = 'id', 'estimated_distance_km', 'ol_number', 'order_date', 'delivery_date', 'notes', 'spbu_id', 'spbu_name', 'items'

class ShippingItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    class Meta:
        model = ShippingItem
        fields = ['product_name', 'quantity', 'unit_price']

class ShippingSerializer(serializers.ModelSerializer):
    
    shippingto = serializers.SerializerMethodField()
    def get_shippingto(self, obj):
        shipping_to_objects = ShippingTo.objects.filter(shipping_id=obj.id)
        return ShippingToSerializer(shipping_to_objects, many=True).data

    license_plate = serializers.SerializerMethodField()
    class Meta:
        model = Shipping
        fields = ['id', 'driver', 'delivery_date', 'truck', 'license_plate', 'status', 'shippingto']  # Added license_plate

    def get_license_plate(self, obj):
        return obj.truck.license_plate if obj.truck else None
    
class TruckDataSerializer(serializers.ModelSerializer):
    brand_nama = serializers.SerializerMethodField()

    def get_brand_nama(self, obj):
        return obj.brand.nama if obj.brand else None

    data_machine_learning = serializers.SerializerMethodField()

    def get_data_machine_learning(self, obj):
        # maintenance_record = get_last_maintenance_record(obj.id)
        truck_id = obj.id
        truck_data = Truck.objects.filter(id=truck_id).first()
        last_maintenance = get_last_maintenance_record(truck_id)
        if last_maintenance:
        # get truck age at service
            if last_maintenance and truck_data and truck_data.year:
                truck_manufacture_date = datetime.date(truck_data.year, 1, 1) # Assumes the truck was made on Jan 1st of its year
                # timedelta does not have a .years attribute. Calculate it from days.
                truck_age_at_service = (last_maintenance.service_date - truck_manufacture_date).days / 365.25
            else:
                truck_age_at_service =  7
        
            # get month of service date
            month_of_service = last_maintenance.service_date.month if last_maintenance else None
            day_of_week = last_maintenance.service_date.weekday() if last_maintenance else None

            # get last ttf km
            last_ttf_km = 0
            last_ttf_days = 0
            if last_maintenance:
                # get last second maintenance record
                i = 1
                second_maintenance_record = get_second_last_maintenance_record(truck_id, i)
                if second_maintenance_record:
                    last_ttf_km = last_maintenance.odometer_reading - second_maintenance_record.odometer_reading
                    last_ttf_days = (last_maintenance.service_date - second_maintenance_record.service_date).days
                    while last_ttf_km < 1000:
                        i += 1
                        second_maintenance_record = get_second_last_maintenance_record(truck_id, i)
                        last_ttf_km = last_maintenance.odometer_reading - second_maintenance_record.odometer_reading
                        last_ttf_days = (last_maintenance.service_date - second_maintenance_record.service_date).days
            
            # get rolling avg 3
            rolling_avg_km_3 = get_rolling_avg_3(truck_id)['ttf_average']
            rolling_avg_km_std = get_rolling_avg_3(truck_id)['ttf_std']
            rolling_avg_days_3 = get_rolling_avg_3(truck_id)['days_average']
            rolling_avg_days_std = get_rolling_avg_3(truck_id)['days_std']


            # get comulative service
            comulative_service = get_commulative_service(truck_id)

            # get model_HINO TYPE
            # get merk
            # merek = truck_data.brand.nama if truck_data and truck_data.brand else None
            # get model
            model = truck_data.model if truck_data else None
            model_name = 'model_' + str(model).upper()  

            payload_data = {
                "truck_age_at_service": int(truck_age_at_service),
                "month_of_service": int(month_of_service),
                "day_of_week": int(day_of_week),
                "last_ttf_km": last_ttf_km,
                "last_ttf_days": int(last_ttf_days),
                "rolling_avg_km_3": rolling_avg_km_3,
                "rolling_std_km_3": rolling_avg_km_std,
                "rolling_avg_days_3": rolling_avg_days_3,
                "rolling_std_days_3": rolling_avg_days_std,
                "cumulative_replacements": int(comulative_service),
                "cumulative_avg_km": get_commulative_km_average(truck_id),
                "cumulative_avg_days": get_commulative_days_average(truck_id),
                "model_" + str(model).upper(): 1
            }

            predicted = get_prediction_from_api(payload_data)
            predicted_days = predicted['predicted_ttf_days']
            predicted_km = predicted['predicted_ttf_km']


            # get next service date
            last_service_date = last_maintenance.service_date if last_maintenance else None
            if last_service_date:
                next_service_date = last_service_date + datetime.timedelta(days=predicted_days)
            else:
                next_service_date = None

            # next service km
            next_service_km = last_maintenance.odometer_reading + predicted_km if last_maintenance else None

            # Django model instances are not directly JSON serializable.
            # Create a dictionary with the data you need.
            truck_data_dict = {
                'id': truck_data.id,
                'year': truck_data.year,
            } if truck_data else None

            return {
                'success': True,
                'truck_data': truck_data_dict,
                'truck_age_at_service': round(truck_age_at_service, 2),
                'month_of_service': month_of_service,
                'last_ttf_km': last_ttf_km,
                'last_ttf_days' : last_ttf_days,
                'rolling_avg_km_3': round(rolling_avg_km_3, 2),
                'rolling_avg_days_3': round(rolling_avg_days_3, 2),
                'count_commulative_service': comulative_service,
                'commulative_km_average': get_commulative_km_average(truck_id),
                'commulative_days_average': get_commulative_days_average(truck_id),
                'truck_name':  "model_" + str(model).upper(),
                'predicted_ttf_days': predicted_days if predicted_days else 0,
                'predicted_ttf_km': predicted_km if predicted_km else 0,
                'next_service_date': next_service_date.strftime('%Y-%m-%d') if next_service_date else None,
                'next_service_km': next_service_km if next_service_km else 0,

            }
        else:
            return {
                'success': False,
                'message': 'Tidak ada riwayat maintenance untuk truk ini.',
            }

    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'brand', 'brand_nama', 'data_machine_learning']

class MttfSerializer(serializers.ModelSerializer):

    mttf = serializers.SerializerMethodField()

    def get_mttf(self, obj):
        truck_id = obj.id
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
            return {
                'mttf_value': round(mttf, 2),
                'labels': labels,
                'values': array_ttf,
                'distribution_name': distribution_name,
                'reliability_score': reliability_score
            }
        
    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'mttf']