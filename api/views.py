from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class LogoutView(TokenBlacklistView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
