from django import forms
from .models import Shipping


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        exclude = ['created_at', 'updated_at']

        labels = {
            'delivery_number': 'Nomor Pengiriman',
            'order_date': 'Tanggal Order',
            'delivery_date': 'Tanggal Pengiriman',
            'status': 'Status',
            'notes': 'Catatan',
            'driver': 'Driver',
            'truck': 'Truck',
        }

        error_messages = {
            'delivery_number': {
                'required': 'Nomor pengiriman harus diisi.',
                'max_length': 'Nomor pengiriman tidak boleh lebih dari 100 karakter.',
                'unique': 'Nomor pengiriman ini sudah digunakan.',
            },
            'order_date': {'required': 'Tanggal order harus diisi.', 'invalid': 'Masukkan format tanggal yang valid.'},
            'status': {'required': 'Status harus dipilih.'},
        }

        widgets = {
            'delivery_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor pengiriman'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'truck': forms.Select(attrs={'class': 'form-select'}),
        }
