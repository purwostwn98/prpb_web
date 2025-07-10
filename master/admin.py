from django.contrib import admin # type: ignore

# Register your models here.
from .models import Merek
from .models import Truck
from .models import Company
from .models import Vendor

admin.site.register(Merek)
admin.site.register(Truck)
admin.site.register(Company)
admin.site.register(Vendor)