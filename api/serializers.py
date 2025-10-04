from rest_framework import serializers
from master.models import Merek

class MerekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merek
        fields = ['id', 'nama', 'deskripsi', 'created_at', 'updated_at']
