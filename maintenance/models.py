from django.db import models # type: ignore
from django.db import transaction # type: ignore
from datetime import datetime
import uuid

# Create your models here.
class Record(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
        ('service', 'Service'),
        ('reset', 'Reset'),
        ('deactivate', 'Deactivate'),
    ]

    STATUS_TYPE_CHOICES = [
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    order_reference = models.CharField(max_length=50, unique=True, editable=False)  # Custom format
    truck = models.ForeignKey('master.Truck', on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=50, choices=MAINTENANCE_TYPE_CHOICES)
    booking_date = models.DateField()
    service_date = models.DateField()
    service_time = models.TimeField(null=True, blank=True)  # Optional field
    odometer_reading = models.IntegerField(blank=True, null=True)  # Optional field
    vendor = models.ForeignKey('master.Vendor', on_delete=models.CASCADE, blank=True, null=True)
    service_location = models.CharField(max_length=250)
    technician_name = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    input_by = models.IntegerField(blank=True, null=True)  # Assuming this references an admin user ID
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_TYPE_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # only work that actually happened tells us the truck's real odometer
    ODOMETER_STATUSES = ('in_progress', 'completed', 'done')

    def save(self, *args, **kwargs):
        self._save_with_reference(*args, **kwargs)
        if self.odometer_reading and self.status in self.ODOMETER_STATUSES:
            from master.odometer import record_odometer
            record_odometer(self.truck, self.odometer_reading, 'maintenance', self.service_date)

    def _save_with_reference(self, *args, **kwargs):
        if self.order_reference:
            return super().save(*args, **kwargs)
        # Generate the order reference in the format MTNE/YEAR/IDNUMBER from the record's own
        # primary key, so concurrent saves can never produce the same number.
        with transaction.atomic():
            self.order_reference = f"TMP/{uuid.uuid4().hex}"
            super().save(*args, **kwargs)
            current_year = datetime.now().year
            self.order_reference = f"MTNE/{current_year}/{self.pk:05d}"  # IDNUMBER padded to 5 digits
            Record.objects.filter(pk=self.pk).update(order_reference=self.order_reference)

    def __str__(self):
        return f"{self.order_reference} - {self.description}"
    
class Log(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=50, choices=Record.STATUS_TYPE_CHOICES)
    log_description = models.TextField()
    updated_by = models.IntegerField()  # Assuming this references an admin user ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.record} - {self.log_type} - {self.log_description} - {self.updated_by}"
    
class RecordItem(models.Model):
    """
    Satu baris pekerjaan dalam record maintenance: komponen apa yang dikerjakan,
    tindakannya, dan (opsional) part yang dipasang.
    """
    ACTION_REPLACE = 'replace'
    ACTION_CHOICES = [
        (ACTION_REPLACE, 'Ganti'),
        ('top_up', 'Tambah / Top Up'),
        ('inspect', 'Inspeksi'),
        ('repair', 'Perbaikan'),
    ]

    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='items')
    component_type = models.ForeignKey('master.ComponentType', on_delete=models.PROTECT, related_name='record_items')
    part = models.ForeignKey('master.Part', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_REPLACE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)  # harga saat transaksi
    notes = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return (self.unit_price or 0) * self.quantity

    def __str__(self):
        return f"{self.record.order_reference} - {self.get_action_display()} {self.component_type} ({self.quantity})"
    
class TruckDeviceModel(models.Model):
    truck = models.ForeignKey('master.Truck', on_delete=models.CASCADE)
    device_model = models.CharField(max_length=255)
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.truck} - {self.device_model}"