from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

# Register your models here.
from .models import Shipping, ShippingTo, ShippingItem
from master.models import Driver, Truck, Spbu, Product

@admin.register(Shipping)
class ShippingAdmin(ModelAdmin):
    search_fields = ('delivery_number', 'driver__name', 'truck__license_plate')
    list_display = ('delivery_number', 'order_date', 'delivery_date', 'status', 'driver', 'truck')
    list_filter = ('status', 'order_date', 'delivery_date')
    fieldsets = [
        ('Informasi Pengiriman', {
            'fields': (
                ('delivery_number', 'status'),
                ('order_date', 'delivery_date'),
                ('driver', 'truck'),
                'notes',
            ),
            'description': 'Informasi dasar mengenai pengiriman.'
        }),
    ]
    inlines = []

class ShippingItemInline(TabularInline):
    model = ShippingItem
    extra = 0
    fields = ['product', 'quantity', 'unit_price']
    # autocomplete_fields = ['product']

@admin.register(ShippingTo)
class ShippingToAdmin(ModelAdmin):
    search_fields = ('shipping__delivery_number', 'spbu__name', 'ol_number')
    list_display = ('shipping', 'spbu', 'estimated_distance_km', 'ol_number', 'order_date', 'delivery_date')
    list_filter = ('order_date', 'delivery_date', 'spbu')
    autocomplete_fields = ['shipping', 'spbu']
    fieldsets = [
        ('Informasi Tujuan Pengiriman', {
            'fields': (
                ('shipping', 'spbu'),
                ('estimated_distance_km', 'ol_number'),
                ('order_date', 'delivery_date'),
                'notes',
            ),
            'description': 'Informasi mengenai tujuan pengiriman.'
        }),
    ]

    inlines = [ShippingItemInline]
    class Media:
        js = ('admin/shippingto_autofill.js',)
    