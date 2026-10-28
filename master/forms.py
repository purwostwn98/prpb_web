from django import forms
from django.utils import timezone # type: ignore
from .models import Merek, Truck, Company, Vendor, Part, Driver, Spbu, Product, ComponentType


class ComponentTypeForm(forms.ModelForm):
    class Meta:
        model = ComponentType
        exclude = ['created_at', 'updated_at']

        labels = {
            'code': 'Kode',
            'name': 'Nama Komponen',
            'category': 'Kategori',
            'unit': 'Satuan',
            'interval_km': 'Interval Penggantian (KM)',
            'interval_days': 'Interval Penggantian (Hari)',
            'warning_km': 'Peringatan Sisa KM',
            'warning_days': 'Peringatan Sisa Hari',
            'track_reliability': 'Hitung MTTF / Reliability',
            'is_active': 'Aktif',
            'description': 'Deskripsi',
        }

        help_texts = {
            'code': 'Kode unik huruf besar tanpa spasi, mis. OLI_MESIN.',
            'interval_km': 'Kosongkan jika tidak dijadwalkan berdasarkan jarak.',
            'interval_days': 'Kosongkan jika tidak dijadwalkan berdasarkan waktu.',
            'warning_km': 'Status "Segera" jika sisa KM kurang dari nilai ini, mis. 2000.',
            'warning_days': 'Status "Segera" jika sisa hari kurang dari nilai ini.',
            'track_reliability': 'Centang jika penggantian komponen ini dianalisis di dashboard truck.',
        }

        error_messages = {
            'code': {'required': 'Kode harus diisi.', 'unique': 'Kode ini sudah digunakan.'},
            'name': {'required': 'Nama komponen harus diisi.'},
            'category': {'required': 'Kategori harus dipilih.'},
        }

        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mis. OLI_MESIN'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mis. Oli Mesin'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'interval_km': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mis. 10000'}),
            'interval_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mis. 180'}),
            'warning_km': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mis. 2000'}),
            'warning_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mis. 14'}),
            'track_reliability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper().replace(' ', '_')


class MerekForm(forms.ModelForm):
    class Meta:
        model = Merek
        fields = ['nama', 'deskripsi']

        labels = {
            'nama': 'Nama Merek',
            'deskripsi': 'Deskripsi Merek',
        }


        error_messages = {
            'nama': {
                'required': 'Nama merek harus diisi.',
                'max_length': 'Nama merek tidak boleh lebih dari 255 karakter.',},
            'deskripsi': {
                'required': 'Deskripsi merek harus diisi.',
                'max_length': 'Deskripsi tidak boleh lebih dari 1000 karakter.',
            }
        }
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama merek'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan deskripsi merek'}),
        }

class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        exclude = ['created_at', 'updated_at', 'odometer_updated_at', 'odometer_source']

        labels = {
            "license_plate": "Nomor Polisi",
            "brand": "Merek Kendaraan",
            "model": "Model Kendaraan",
            "year": "Tahun Kendaraan",
            "capacity": "Kapasitas (liter)",
            "current_odometer": "Odometer Saat Ini (km)",
            "status": "Status Kendaraan",
            "acquisition_date": "Tanggal Akuisisi",
            "engine_number": "Nomor Mesin",
            "chassis_number": "Nomor Rangka",
        }
        error_messages = {
            "license_plate" :{
                'required': 'Nomor polisi harus diisi.',
                'max_length': 'Nomor polisi tidak boleh lebih dari 25 karakter.',
            },
            'brand':{
                'required' : 'Merek kendaraan harus diisi.',
                'max_length': 'Merek kendaraan tidak boleh lebih dari 255 karakter.',
            },
            'model': {
                'required': 'Model kendaraan harus diisi.',
                'max_length': 'Model kendaraan tidak boleh lebih dari 200 karakter.',
            },
            'year': {
                'required': 'Tahun kendaraan harus diisi.',
                'invalid': 'Masukkan tahun yang valid.',
            },
            'capacity':{
                'required' : 'kapasitas kendaraaan harus diisi.',
                'invalid': 'Masukkan format data kapasitas yang sesuai.',
            },
            'current_odometer' :{
                'required': 'Odometer saat ini harus diisi.',
                'invalid': 'Masukkan format data odometer yang sesuai.',
            },
            'status':{
                'required': 'Status kendaraan harus diisi.',
            },
            'acquisition_date': {
                'required': 'Tanggal akuisisi harus diisi.',
                'invalid': 'Masukkan format tanggal yang valid (YYYY-MM-DD).',
            },
            'engine_number': {
                'required': 'Nomor mesin harus diisi.',
                'max_length': 'Nomor mesin tidak boleh lebih dari 255 karakter.',
            },
            'chassis_number': {
                'required': 'Nomor rangka harus diisi.',
                'max_length': 'Nomor rangka tidak boleh lebih dari 255 karakter.',
            },
        }
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor polisi'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan model kendaraan'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan tahun kendaraan'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan kapasitas (liter)'}),
            'current_odometer': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan odometer saat ini'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor mesin'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor rangka'}),
        }


    def save(self, commit=True):
        truck = super().save(commit=False)
        if 'current_odometer' in self.changed_data:
            # admins may also lower the value here to correct a wrong reading
            truck.odometer_updated_at = timezone.now()
            truck.odometer_source = 'manual'
        if commit:
            truck.save()
            self.save_m2m()
        return truck

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ['created_at', 'updated_at']
        labels = {
            'name': 'Nama Perusahaan',
            'address': 'Alamat Perusahaan',
            'phone_number': 'Nomor Telepon',
            'email': 'Email Perusahaan',
            'logo': 'Logo Perusahaan',
        }
        error_messages={
            'name':{
                'required': 'Nama perusahaan harus diisi.',
                'max_length': 'Nama perusahaan tidak boleh lebih dari 255 karakter.',
            },
            'address': {
                'required': 'Alamat perusahaan harus diisi.',
                'max_length': 'Alamat tidak boleh lebih dari 1000 karakter.',
            },
            'phone_number':{
                'required': 'Nomor telepon harus diisi.',
                'max_length': 'Nomor telepon tidak boleh lebih dari 20 karakter.',
            },
            'email':{
                'required' : 'Email perusahaan harus diisi.',
                'invalid' : 'Masukkan format email yang valid dengan "@".',
            },
            'logo': {
                'invalid': 'Unggah file logo yang valid (format gambar seperti PNG, JPEG, atau GIF).',
            }
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama perusahaan'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan alamat lengkap perusahaan'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon perusahaan'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan alamat email perusahaan'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        exclude = ['created_at', 'updated_at']

        labels = {
            'name': 'Nama Vendor',
            'address': 'Alamat Vendor',
            'phone_number': 'Nomor Telepon',
            'email': 'Email Vendor',
            'logo': 'Logo Vendor',
        }

        help_texts = {
            'name': 'Masukkan nama vendor.',
            'address': 'Masukkan alamat lengkap vendor.',
            'phone_number': 'Masukkan nomor telepon vendor.',
            'email': 'Masukkan alamat email vendor.',
            'logo': 'Unggah logo vendor (opsional).',
        }

        error_messages={
            'name':{
                'required': 'Nama vendor harus diisi.',
                'max_length': 'Nama vendor tidak boleh lebih dari 255 karakter.',
            },
            'address':{
                'required': 'Alamat vendor harus diisi.',
                'max_length': 'Alamat tidak boleh lebih dari 1000 karakter.',
            },
            'phone_number':{
                'required': 'Nomor telepon harus diisi.',
                'max_length': 'Nomor telepon tidak boleh lebih dari 20 karakter.',
            },
            'email':{
                'required': 'Email vendor harus diisi.',
                'invalid': 'Masukkan format email yang valid dengan "@".',
            },
            'logo': {
                'invalid': 'Unggah file logo yang valid (format gambar seperti PNG, JPEG, atau GIF).',
            }
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama vendor'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan alamat lengkap vendor'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon vendor'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan alamat email vendor'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        exclude = ['created_at', 'updated_at']

        labels = {
            'name': 'Nama Part',
            'part_code': 'Kode Part',
            'component_type': 'Jenis Komponen',
            'description': 'Deskripsi Part',
            'quantity': 'Kuantitas',
            'unit_price': 'Harga Satuan',
            'vendor': 'Vendor',
        }

        help_texts = {
            'name': 'Masukkan nama part.',
            'part_code': 'Masukkan kode unik untuk part.',
            'component_type': 'Pilih jenis komponen. Tambah jenis baru di menu Master > Jenis Komponen.',
            'description': 'Masukkan deskripsi singkat tentang part.',
            'quantity': 'Masukkan jumlah part yang tersedia.',
            'unit_price': 'Masukkan harga satuan untuk part.',
            #'vendor': 'Pilih vendor yang menyediakan part.',
        }

        error_messages = {
            'name':{
                'required' : 'Nama part harus diisi.',
                'max_length': 'Nama part tidak boleh lebih dari 255 karakter.',
            },
            'part_code': {
                'required': 'Kode part harus diisi.',
                'max_length': 'Kode part tidak boleh lebih dari 100 karakter.',
                #'unique': 'Kode part ini sudah ada, silakan gunakan kode yang berbeda.',
            },
            'component_type': {
                'required': 'Jenis komponen harus dipilih.',
            },
            'description':{
                'required' : 'Deskripsi part harus diisi.',
                'max_length': 'Deskripsi tidak boleh lebih dari 1000 karakter.',
            },
            'quantity':{
                'required' : 'Kuantitas part harus diisi',
                'invalid' : 'Masukkan format angka.'
            },
            'unit_price':{
                'required' : 'Harga satuan part perlu diisi.',
                'invalid' : 'Masukkan format angka.'
            },
            #'vendor':{}
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama part'}),
            'part_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan kode part'}),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan deskripsi part'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan kuantitas'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan harga satuan'}),
            'vendor': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ['created_at', 'updated_at']

        labels = {
            'name': 'Nama Driver',
            'user': 'Akun User',
            'license_number': 'Nomor SIM',
            'phone_number': 'Nomor Telepon',
            'years_old': 'Usia',
            'address': 'Alamat',
        }

        error_messages = {
            'name': {
                'required': 'Nama driver harus diisi.',
                'max_length': 'Nama tidak boleh lebih dari 255 karakter.',
            },
            'user': {
                'required': 'Akun user harus dipilih.',
                'unique': 'User ini sudah terhubung dengan driver lain.',
            },
            'license_number': {
                'required': 'Nomor SIM harus diisi.',
                'max_length': 'Nomor SIM tidak boleh lebih dari 100 karakter.',
                'unique': 'Nomor SIM ini sudah terdaftar.',
            },
            'phone_number': {
                'required': 'Nomor telepon harus diisi.',
                'max_length': 'Nomor telepon tidak boleh lebih dari 20 karakter.',
            },
            'years_old': {
                'required': 'Usia harus diisi.',
                'invalid': 'Masukkan angka yang valid.',
            },
            'address': {
                'required': 'Alamat harus diisi.',
            },
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama driver'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor SIM'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon'}),
            'years_old': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan usia'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan alamat lengkap'}),
        }


class SpbuForm(forms.ModelForm):
    class Meta:
        model = Spbu
        exclude = ['created_at', 'updated_at']

        labels = {
            'code': 'Kode SPBU',
            'name': 'Nama SPBU',
            'city': 'Kota',
            'address': 'Alamat',
            'address2': 'Alamat 2',
            'owner': 'Pemilik',
            'latitude': 'Garis Lintang',
            'longitude': 'Garis Bujur',
            'mdpl': 'MDPL',
            'distance': 'Jarak dari TBBM',
            'phone_number': 'Nomor Telepon',
        }

        error_messages = {
            'code': {
                'required': 'Kode SPBU harus diisi.',
                'max_length': 'Kode SPBU tidak boleh lebih dari 50 karakter.',
                'unique': 'Kode SPBU ini sudah ada.',
            },
        }

        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan kode SPBU'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama SPBU'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan kota'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Masukkan alamat'}),
            'address2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat tambahan (opsional)'}),
            'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan pemilik'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Contoh: -7.560000'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Contoh: 110.830000'}),
            'mdpl': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Meter di atas permukaan laut'}),
            'distance': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Jarak dari TBBM ke SPBU'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor telepon'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

        labels = {
            'name': 'Nama Produk',
            'description': 'Deskripsi',
            'price': 'Harga',
            'stock': 'Stok',
        }

        error_messages = {
            'name': {
                'required': 'Nama produk harus diisi.',
                'max_length': 'Nama produk tidak boleh lebih dari 255 karakter.',
            },
            'description': {
                'required': 'Deskripsi harus diisi.',
            },
            'price': {
                'required': 'Harga harus diisi.',
                'invalid': 'Masukkan angka yang valid.',
            },
            'stock': {
                'required': 'Stok harus diisi.',
                'invalid': 'Masukkan angka yang valid.',
            },
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama produk'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan deskripsi produk'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan harga'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan stok'}),
        }
