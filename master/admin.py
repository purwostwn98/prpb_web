from django.contrib import admin
from unfold.admin import ModelAdmin

# Register your models here.
from .models import Merek
from .models import Truck
from .models import Company
from .models import Vendor
from .models import Part

@admin.register(Truck)
class TruckAdmin(ModelAdmin):
    search_fields = ('license_plate', 'model', 'brand__nama')
    list_display = ('license_plate', 'brand', 'model', 'status')
    list_filter = ('status', 'brand')

admin.site.register(Merek, ModelAdmin)
admin.site.register(Company, ModelAdmin)
admin.site.register(Vendor, ModelAdmin)
admin.site.register(Part, ModelAdmin)