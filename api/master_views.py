from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from maintenance.analytics import STATUS_OVERDUE, STATUS_SOON, component_due_list, warning_components
from delivery.models import Shipping, ShippingTo
from master.models import Driver, Merek, Truck
from .serializers import MerekSerializer, PressureChartDataSerializer, ShippingSerializer, ShippingToSerializer, TruckDataSerializer, TruckSerializer, MttfSerializer, UserDriverSerializer, UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

class MerekViewSet(viewsets.ModelViewSet):
    queryset = Merek.objects.all()
    serializer_class = MerekSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        driver = self.request.query_params.get('driver')
        queryset = Shipping.objects.all()
        if driver is not None:
            queryset = queryset.filter(driver=driver)
        return queryset
    
class UserDriverViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserDriverSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            return self.User.objects.filter(id=user_id)
        return self.User.objects.all()
    
class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.request.query_params.get('username')
        if username is not None:
            return self.User.objects.filter(username=username)
        return self.User.objects.all()


class TruckBaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TruckSerializer
    def get_queryset(self):
        """
        Returns a queryset of Truck objects, optionally filtered by truck_id from query parameters.
        """
        truck_id = self.request.query_params.get('truck_id')
        if truck_id is not None:
            return Truck.objects.filter(id=truck_id)
        return Truck.objects.all()
    
class TruckDataViewSet(TruckBaseViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Truck.objects.all()
    serializer_class = TruckDataSerializer

    def get_queryset(self):
        truck_id = self.request.query_params.get('truck_id')
        if truck_id is not None:
            return Truck.objects.filter(id=truck_id)
        return Truck.objects.all()
    
class MttfViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    # queryset = Truck.objects.all()
    serializer_class = MttfSerializer
    def get_queryset(self):
        truck_id = self.request.query_params.get('truck_id')
        if truck_id is not None:
            return Truck.objects.filter(id=truck_id)
        return Truck.objects.all()
    
class ShippingToViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingToSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        shipping_id = self.request.query_params.get('shipping_id')
        queryset = ShippingTo.objects.all()
        if shipping_id is not None:
            queryset = queryset.filter(shipping_id=shipping_id)
        return queryset
    
class PressureChartDataViewSet(viewsets.ModelViewSet):
    serializer_class = PressureChartDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        truck_id = self.request.query_params.get('truck_id')
        queryset = Truck.objects.all()
        if truck_id is not None:
            queryset = queryset.filter(id=truck_id)
        return queryset

    

class DriverAlertsView(APIView):
    """
    Maintenance warnings for the driver app: components that are overdue or due soon
    (same rules as the web Early Warning page) and trucks whose km is out of date.
    A driver sees the trucks of their own shipments; other users see every operating truck.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trucks = Truck.objects.exclude(status='inactive')
        driver = Driver.objects.filter(user=request.user).first()
        if driver:
            trucks = trucks.filter(shipping__driver=driver).distinct()

        alerts = []
        stale_trucks = {}
        for component in warning_components():
            for row in component_due_list(component, trucks):
                truck = row['truck']
                if row['odometer_stale']:
                    stale_trucks[truck.pk] = (truck, row['odometer_age_days'])
                if row['status'] not in (STATUS_OVERDUE, STATUS_SOON):
                    continue
                alerts.append({
                    'type': 'component',
                    'truck_id': truck.pk,
                    'license_plate': truck.license_plate,
                    'component_code': component.code,
                    'component_name': component.name,
                    'status': row['status'],
                    'status_label': row['status_label'],
                    'remaining_km': row['remaining_km'],
                    'remaining_days': row['remaining_days'],
                    'due_km': row['due_km'],
                    'due_date': row['due_date'],
                    'current_odometer': truck.current_odometer,
                })
        alerts.sort(key=lambda a: (a['status'] != STATUS_OVERDUE, a['license_plate'], a['component_name']))

        # the km countdown is only as fresh as the truck's last reported odometer
        for truck, age_days in sorted(stale_trucks.values(), key=lambda t: t[0].license_plate):
            alerts.append({
                'type': 'odometer',
                'truck_id': truck.pk,
                'license_plate': truck.license_plate,
                'status': 'info',
                'status_label': 'Perlu diperbarui',
                'odometer_age_days': age_days,
                'current_odometer': truck.current_odometer,
            })
        return Response({'alerts': alerts})
