from django import forms
from .models import Shipping, ShippingTo, ShippingItem


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


class ShippingToForm(forms.ModelForm):
    class Meta:
        model = ShippingTo
        exclude = ['created_at', 'updated_at']

        labels = {
            'shipping': 'Pengiriman (No. Pengiriman)',
            'spbu': 'SPBU Tujuan',
            'estimated_distance_km': 'Estimasi Jarak (KM)',
            'ol_number': 'Nomor OL',
            'order_date': 'Tanggal Order',
            'delivery_date': 'Tanggal Kirim',
            'notes': 'Catatan',
        }

        error_messages = {
            'shipping': {'required': 'Pengiriman harus dipilih.'},
            'spbu': {'required': 'SPBU tujuan harus dipilih.'},
            'estimated_distance_km': {
                'required': 'Estimasi jarak harus diisi.',
                'invalid': 'Masukkan angka yang valid.',
            },
            'ol_number': {
                'required': 'Nomor OL harus diisi.',
                'max_length': 'Nomor OL tidak boleh lebih dari 100 karakter.',
            },
            'order_date': {'required': 'Tanggal order harus diisi.', 'invalid': 'Masukkan format tanggal yang valid.'},
        }

        widgets = {
            'shipping': forms.Select(attrs={'class': 'form-select'}),
            'spbu': forms.Select(attrs={'class': 'form-select select2'}),
            'estimated_distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Masukkan estimasi jarak (KM)'}),
            'ol_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor OL'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
        }


class ShippingItemForm(forms.ModelForm):
    class Meta:
        model = ShippingItem
        fields = ['product', 'quantity', 'unit_price']

        labels = {
            'product': 'Produk',
            'quantity': 'Kuantitas',
            'unit_price': 'Harga Satuan',
        }

        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kuantitas'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Harga satuan'}),
        }


ShippingItemFormSet = forms.inlineformset_factory(
    ShippingTo,
    ShippingItem,
    form=ShippingItemForm,
    extra=1,
    can_delete=True,
)
