from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

# Register your models here.
from .models import *
from master.models import Truck

class RecordPartsInline(TabularInline):
    model = RecordParts
    extra = 0
    fields = ['record','part', 'quantity']
    readonly_fields = ['record']
@admin.register(Record)
class RecordAdmin(ModelAdmin):
    list_display = ['order_reference', 'maintenance_type', 'truck_license_plate']
    @display(description='Truck License Plate')
    def truck_license_plate(self, obj):
        return obj.truck.license_plate if obj.truck else "-"
    search_fields = ['order_reference', 'maintenance_type', 'truck__license_plate']
    list_filter = ['maintenance_type']
    ordering = ['order_reference']
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing record
            return ['order_reference', 'truck']
        else:  # adding new record
            return ['order_reference']
    autocomplete_fields = ['truck']
    fieldsets = [
        ('Informasi Record', {
            'fields': ['order_reference', 'maintenance_type', 'status', 'truck'],
            'description': 'Informasi dasar mengenai record maintenance.'
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new records
            super().save_model(request, obj, form, change)
            Log.objects.create(
                record=obj,
                log_type=obj.status,
                log_description=f"Record {obj.order_reference} created with status {obj.status}.",
                updated_by=request.user.id
            )
        else:  # For existing records
            original_obj = self.model.objects.get(pk=obj.pk)
            super().save_model(request, obj, form, change)
            if original_obj.status != obj.status:
                Log.objects.create(
                    record=obj,
                    log_type=obj.status,
                    log_description=f"Record {obj.order_reference} status changed from {original_obj.status} to {obj.status}.",
                    updated_by=request.user.id
                )
            else:
                Log.objects.create(
                    record=obj,
                    log_type=obj.status,
                    log_description=f"Record {obj.order_reference} updated.",
                    updated_by=request.user.id
                )
    # Add the inline to your RecordAdmin
    inlines = [RecordPartsInline]
    


    # Optionally, you can exclude 'record' if it's a ForeignKey to Record and handled automatically


        

# admin.site.register(Record)
admin.site.register(Log)
admin.site.register(RecordParts)