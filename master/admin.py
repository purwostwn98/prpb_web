from django.contrib import admin
from unfold.admin import ModelAdmin

# Register your models here.
from .models import *

@admin.register(Truck)
class TruckAdmin(ModelAdmin):
    search_fields = ('license_plate', 'model', 'brand__nama')
    list_display = ('license_plate', 'brand', 'model', 'status')
    list_filter = ('status', 'brand')
    fieldsets = [
        ('Informasi Kendaraan', {
            'fields': (
                ('license_plate', 'brand'),
                ('model', 'year'),
                ('capacity', 'current_odometer'),
                ('acquisition_date', 'engine_number'),
                ('chassis_number', 'status'),
            ),
            'description': 'Informasi dasar mengenai kendaraan.'
        }),
    ]

@admin.register(Part)
class PartAdmin(ModelAdmin):
    search_fields = ('part_code', 'name')
    list_display = ('part_code', 'name', 'jenis_part', 'quantity')
    list_filter = ('jenis_part',)
    fieldsets = [
        ('Informasi Part', {
            'fields': (
                ('part_code', 'name'),
                ('jenis_part', 'unit_price', 'quantity'),
                ('description', 'vendor'),
            ),
            'description': 'Informasi dasar mengenai part.'
        }),
    ]

@admin.register(Driver)
class DriverAdmin(ModelAdmin):
    search_fields = ('name', 'license_number')
    list_display = ('name', 'license_number', 'phone_number')
    list_filter = ()
    fieldsets = [
        ('Informasi Driver', {
            'fields': (
                ('user', 'name'),
                ('years_old', 'license_number'),
                ('phone_number', 'address'),
            ),
            'description': 'Informasi dasar mengenai driver.'
        }),
    ]

@admin.register(Spbu)
class SpbuAdmin(ModelAdmin):
    search_fields = ('code', 'name', 'address', 'owner')
    list_display = ('code', 'name', 'address', 'owner')
    ordering = ('-name',)
    list_filter = ('city', 'owner')
    list_per_page = 30
    fieldsets = [
        ('Informasi SPBU', {
            'fields': (
                ('code', 'name'),
                ('owner', 'city'),
                ('address', 'address2'),
                ('latitude', 'longitude'),
                ('mdpl', 'distance'),
                ('phone_number',),
            ),
            'description': 'Informasi dasar mengenai SPBU.'
        }),
    ]

admin.site.register(Merek, ModelAdmin)
admin.site.register(Company, ModelAdmin)
admin.site.register(Vendor, ModelAdmin)
