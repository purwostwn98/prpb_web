from django import forms
from .models import Record, TruckDeviceModel


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        exclude = ['created_at', 'updated_at', 'input_by']

        labels = {
            'truck': 'Truck',
            'maintenance_type': 'Jenis Maintenance',
            'booking_date': 'Tanggal Booking',
            'service_date': 'Tanggal Service',
            'service_time': 'Jam Service',
            'odometer_reading': 'Odometer (KM)',
            'vendor': 'Vendor',
            'service_location': 'Lokasi Service',
            'technician_name': 'Nama Teknisi',
            'cost': 'Biaya',
            'description': 'Deskripsi',
            'notes': 'Catatan',
            'status': 'Status',
        }

        error_messages = {
            'truck': {'required': 'Truck harus dipilih.'},
            'maintenance_type': {'required': 'Jenis maintenance harus dipilih.'},
            'booking_date': {'required': 'Tanggal booking harus diisi.', 'invalid': 'Masukkan format tanggal yang valid.'},
            'service_date': {'required': 'Tanggal service harus diisi.', 'invalid': 'Masukkan format tanggal yang valid.'},
            'service_location': {'required': 'Lokasi service harus diisi.', 'max_length': 'Lokasi service tidak boleh lebih dari 250 karakter.'},
            'technician_name': {'required': 'Nama teknisi harus diisi.', 'max_length': 'Nama teknisi tidak boleh lebih dari 200 karakter.'},
            'cost': {'invalid': 'Masukkan format angka yang valid.'},
            'status': {'required': 'Status harus dipilih.'},
        }

        widgets = {
            'truck': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan pembacaan odometer'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'service_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan lokasi service'}),
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama teknisi'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan biaya'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan deskripsi'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TruckDeviceForm(forms.ModelForm):
    class Meta:
        model = TruckDeviceModel
        fields = ['truck', 'device_model']

        labels = {
            'truck': 'Truck',
            'device_model': 'Device Model / ID',
        }

        error_messages = {
            'truck': {'required': 'Truck harus dipilih.'},
            'device_model': {
                'required': 'Device model harus diisi.',
                'max_length': 'Device model tidak boleh lebih dari 255 karakter.',
            },
        }

        widgets = {
            'truck': forms.Select(attrs={'class': 'form-select'}),
            'device_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: ACL-0001-AT'}),
        }
