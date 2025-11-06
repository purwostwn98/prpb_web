from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .master_views import * 

router = DefaultRouter()
router.register(r'merek', MerekViewSet, basename='merek')
router.register(r'shipping', ShippingViewSet, basename='shipping')
router.register(r'truck', TruckBaseViewSet, basename='truck')
router.register(r'user-driver', UserDriverViewSet, basename='user-driver')
router.register(r'user', UserViewSet, basename='user')
router.register(r'truck-data-ml', TruckDataViewSet, basename='truck-data-ml')
router.register(r'truck-mttf', MttfViewSet, basename='truck-mttf')



urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('', include(router.urls)),
]
