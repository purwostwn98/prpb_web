from rest_framework import viewsets, permissions
from master.models import Merek
from .serializers import MerekSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class MerekViewSet(viewsets.ModelViewSet):
    queryset = Merek.objects.all()
    serializer_class = MerekSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
