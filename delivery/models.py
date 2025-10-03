from django.db import models

# Create your models here.
class Shipping(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('on_progress', 'On Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    delivery_number = models.CharField(max_length=100, unique=True)
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    driver = models.ForeignKey('master.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    truck = models.ForeignKey('master.Truck', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.delivery_number} - {self.truck.license_plate} - {self.status}"

class ShippingTo(models.Model):
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='destinations')
    spbu = models.ForeignKey('master.Spbu', on_delete=models.CASCADE)
    estimated_distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    ol_number = models.CharField(max_length=100)
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.spbu.name} - {self.spbu.address}"
    
class ShippingItem(models.Model):
    shippingto = models.ForeignKey(ShippingTo, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('master.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"SPBU {self.shippingto.spbu.name} - {self.product.name} - {self.quantity} units"