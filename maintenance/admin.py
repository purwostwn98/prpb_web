from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Record)
admin.site.register(Log)
admin.site.register(RecordParts)