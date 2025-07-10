from django.db import models # type: ignore
from datetime import datetime

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

    def save(self, *args, **kwargs):
        if not self.order_reference:
            # Generate the order reference in the format MTNE/YEAR/IDNUMBER
            current_year = datetime.now().year
            last_record = Record.objects.order_by('id').last()
            next_id = last_record.id + 1 if last_record else 1
            self.order_reference = f"MTNE/{current_year}/{next_id:05d}"  # IDNUMBER padded to 5 digits
        super().save(*args, **kwargs)

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
    

class RecordParts(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)  # Links to the Record model
    part = models.ForeignKey('master.Part', on_delete=models.CASCADE)  # Links to the Part model
    quantity = models.IntegerField(default=1)  # Optional: Add quantity if needed
    added_at = models.DateTimeField(auto_now_add=True)  # Optional: Track when the part was added

    def __str__(self):
        return f"{self.record.order_reference} - {self.part.name} - Quantity: {self.quantity}"
    
    ##      BELUM DI MIGRASI