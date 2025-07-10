from django.db import models # type: ignore

# Merek == Brand.
class Merek(models.Model):
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nama} - {self.deskripsi}"
    
class Truck(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]

    license_plate = models.CharField(max_length=25, unique=True)
    brand = models.ForeignKey(Merek, on_delete=models.CASCADE)
    model = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text='Kapasitas dalam liter')
    current_odometer = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    acquisition_date = models.DateField(null=True, blank=True)
    engine_number = models.CharField(max_length=255, blank=True, null=True)
    chassis_number = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.brand.nama) + " " + str(self.license_plate) + " - " + str(self.model) + " (" + str(self.status) + ")"
    
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address}"
    
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address}"
    
class Part(models.Model):
    JENIS_PART_CHOICES = [
        ('filer', 'Filer'),
        # ('oli', 'Oli'),
        # ('ban', 'Ban'),
        # ('suku_cadang', 'Suku Cadang'),
        # ('lainnya', 'Lainnya')
    ]
    name = models.CharField(max_length=255)
    part_code = models.CharField(max_length=100, unique=True)
    jenis_part = models.CharField(max_length=100, choices=JENIS_PART_CHOICES)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    vendor = models.ManyToManyField(Vendor, related_name='parts')   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.part_code} - {self.name}"