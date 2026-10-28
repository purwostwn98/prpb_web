from django.db import models # type: ignore


# Merek == Brand.
class Merek(models.Model):
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama # perubahan: mengembalikan nama merek saja
    
class Truck(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]

    ODOMETER_SOURCE_CHOICES = [
        ('manual', 'Input Manual'),
        ('maintenance', 'Record Maintenance'),
        ('shipping', 'Pengiriman (Driver)'),
        ('gps', 'GPS'),
    ]

    license_plate = models.CharField(max_length=25, unique=True)
    brand = models.ForeignKey(Merek, on_delete=models.CASCADE)
    model = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text='Kapasitas dalam liter')
    current_odometer = models.PositiveIntegerField()
    odometer_updated_at = models.DateTimeField(null=True, blank=True, help_text='Waktu km terakhir diperbarui')
    odometer_source = models.CharField(max_length=20, choices=ODOMETER_SOURCE_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    acquisition_date = models.DateField(null=True, blank=True)
    engine_number = models.CharField(max_length=255, blank=True, null=True)
    chassis_number = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # plate first (what users search for); skip the brand when the model name already contains it
        name = self.model if self.brand.nama.lower() in self.model.lower() else f"{self.brand.nama} {self.model}"
        status = '' if self.status == 'active' else f" ({self.get_status_display()})"
        return f"{self.license_plate} – {name}{status}"
    
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='static/company_logos/', null=True, blank=True)
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
    
class ComponentType(models.Model):
    """
    Jenis komponen yang dirawat/diganti pada truck (Filter Solar Atas, Oli Mesin, ...).
    Analitik maintenance (MTTF, reliability, prediksi) dihitung per jenis komponen.
    """
    CATEGORY_CHOICES = [
        ('filter_solar', 'Filter Solar'),
        ('filter', 'Filter Lainnya'),
        ('oli', 'Oli / Pelumas'),
        ('ban', 'Ban'),
        ('rem', 'Rem'),
        ('kelistrikan', 'Kelistrikan / Aki'),
        ('lainnya', 'Lainnya'),
    ]
    UNIT_CHOICES = [
        ('pcs', 'Pcs'),
        ('liter', 'Liter'),
        ('set', 'Set'),
    ]

    code = models.CharField(max_length=50, unique=True, help_text='Kode unik, mis. OLI_MESIN')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    interval_km = models.PositiveIntegerField(null=True, blank=True, help_text='Interval penggantian (KM)')
    interval_days = models.PositiveIntegerField(null=True, blank=True, help_text='Interval penggantian (hari)')
    warning_km = models.PositiveIntegerField(null=True, blank=True, help_text='Peringatan jika sisa KM kurang dari nilai ini')
    warning_days = models.PositiveIntegerField(null=True, blank=True, help_text='Peringatan jika sisa hari kurang dari nilai ini')
    track_reliability = models.BooleanField(default=True, help_text='Ikut dihitung MTTF / reliability')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def has_ml_prediction(self):
        # the prediction model was trained on fuel filter replacements only
        return self.category == 'filter_solar'

    def __str__(self):
        return self.name


class Part(models.Model):
    name = models.CharField(max_length=255)
    part_code = models.CharField(max_length=100, unique=True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.PROTECT, related_name='parts')
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    vendor = models.ManyToManyField(Vendor, related_name='parts')   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.part_code} - {self.name}"
    
class Driver(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, unique=True)
    license_number = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    years_old = models.PositiveIntegerField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.license_number}"
    
class Spbu(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    address2 = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text='Garis lintang', null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text='Garis bujur', null=True, blank=True)
    mdpl = models.DecimalField(max_digits=10, decimal_places=2, help_text='Meter di atas permukaan laut', null=True, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, help_text='Jarak dari tbbm ke spbu', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.distance} - {self.name} - {self.address}"
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name