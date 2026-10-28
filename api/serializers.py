from datetime import date, timedelta, datetime
from django.http import JsonResponse
from rest_framework import serializers
from master.models import Merek, Truck
from master.models import Driver
from core.utils import *
from delivery.models import Shipping, ShippingItem, ShippingTo
from delivery.validators import shipping_assignment_errors
from master.odometer import odometer_error
from maintenance.analytics import fitted_mttf, get_component, next_service

from maintenance.models import Record as MaintenanceRecord, TruckDeviceModel  # Add this import at the module level
from django.contrib.auth import get_user_model

import numpy as np # type: ignore


def component_from_request(context):
    """Component chosen with ?component=CODE (defaults to the fuel filter)."""
    request = context.get('request')
    return get_component(request.query_params.get('component') if request else None)


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
        fields = ['id', 'license_plate', 'brand', 'brand_nama', 'model', 'year']

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
    def get_license_plate(self, obj):
        return obj.truck.license_plate if obj.truck else None
    
    model = serializers.SerializerMethodField()
    def get_model(self, obj):
        return obj.truck.model if obj.truck else None
    
    class Meta:
        model = Shipping
        fields = ['id', 'driver', 'delivery_date', 'truck', 'model', 'license_plate', 'status', 'odometer_end', 'shippingto']  # Added license_plate

    def validate(self, attrs):
        # partial updates (PATCH) only send changed fields, so fall back to the stored values
        instance = self.instance
        errors = shipping_assignment_errors(
            truck=attrs.get('truck', instance.truck if instance else None),
            driver=attrs.get('driver', instance.driver if instance else None),
            status=attrs.get('status', instance.status if instance else 'draft'),
            exclude_pk=instance.pk if instance else None,
        )
        odometer_end = attrs.get('odometer_end')
        if odometer_end is not None and (instance is None or odometer_end != instance.odometer_end):
            error = odometer_error(attrs.get('truck', instance.truck if instance else None), odometer_end)
            if error:
                errors['odometer_end'] = error
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    
    
class TruckDataSerializer(serializers.ModelSerializer):
    brand_nama = serializers.SerializerMethodField()

    def get_brand_nama(self, obj):
        return obj.brand.nama if obj.brand else None

    data_machine_learning = serializers.SerializerMethodField()

    def get_data_machine_learning(self, obj):
        result = next_service(obj, component_from_request(self.context), default_truck_age=7)
        if result is None:
            return {
                'success': False,
                'message': 'Tidak ada riwayat maintenance untuk truk ini.',
            }
        return {'success': True, **result}

    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'brand', 'brand_nama', 'data_machine_learning']

class MttfSerializer(serializers.ModelSerializer):

    mttf = serializers.SerializerMethodField()

    def get_mttf(self, obj):
        result = fitted_mttf(obj.id, component_from_request(self.context))
        return {
            'mttf_value': round(result['mttf'], 2),
            'labels': result['labels'],
            'values': result['values'],
            'distribution_name': result['distribution_name'],
            'reliability_score': result['reliability_score'],
        }

    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'mttf']

class PressureChartDataSerializer(serializers.ModelSerializer):

    pressure_chart_data = serializers.SerializerMethodField()

    def get_pressure_chart_data(self, obj):
        # Example static data for pressure chart
        truck_id = obj.id
        truckDevice = TruckDeviceModel.objects.filter(truck__id=truck_id).first()
        if not truckDevice:
            transformed_data = [{
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day': datetime.now().strftime('%a'),
                'pressure': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            }]
            return transformed_data
        
        device_id = truckDevice.device_model
        response = get_fuel_filter_pressure_from_api(device_id)
        results = response.get('results', [])
        # Transform each result
        transformed_data = []
        
        for item in results:
            # Extract date from timestamp
            date_str = item['timestamp'].split('T')[0]
            
            # Get day name
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%a')  # Short day name (Mon, Tue, etc.)
            
            # Get pressure value (absolute value)
            pressure = round(abs(float(item['pressure_value'])))
            
            transformed_data.append({
                'date': date_str,
                'day': day_name,
                'pressure': pressure,
                'timestamp': item['timestamp']
            })
        
        return transformed_data
    
    period = serializers.SerializerMethodField()
    def get_period(self, obj):
        return "7t"
    
    data_collected_at = serializers.SerializerMethodField()
    def get_data_collected_at(self, obj):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'period', 'data_collected_at', 'pressure_chart_data']