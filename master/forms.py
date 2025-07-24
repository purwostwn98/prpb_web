from django import forms
from .models import Merek, Truck, Company, Vendor, Part


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
        exclude = ['created_at', 'updated_at']

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

        help_texts = {
            "license_plate": "Masukkan nomor polisi kendaraan.",
            "brand":"Masukkan nama merek kendaraan.",
            "model": "Masukkan model kendaraan.",
            "year": "Masukkan tahun kendaraan.",
            "capacity" :"Masukkan kapasitas kendaraan (liter).",
            "current_odometer": "Masukkan odometer saat ini (km).",
            "status": "Pilih status kendaraan.",
            "acquisition_date": "Masukkan tanggal akuisisi kendaraan (YYYY-MM-DD).",
            "engine_number": "Masukkan nomor mesin kendaraan.",
            "chassis_number": "Masukkan nomor rangka kendaraan.",
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
        # fields = [
        #     'license_plate', 'brand', 'model', 'year', 
        #     'capacity', 'current_odometer', 'status', 
        #     'acquisition_date', 'engine_number', 'chassis_number'
        # ]
        #widgets = {
        #    'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
        #    'brand': forms.Select(attrs={'class': 'form-control'}),
        #    'model': forms.TextInput(attrs={'class': 'form-control'}),
        #    'year': forms.NumberInput(attrs={'class': 'form-control'}),
        #    'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        #    'current_odometer': forms.NumberInput(attrs={'class': 'form-control'}),
        #    'status': forms.Select(attrs={'class': 'form-control'}),
        #    'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        #    'engine_number': forms.TextInput(attrs={'class': 'form-control'}),
        #    'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
        #}


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

        help_texts = {
            'name': 'Masukkan nama perusahaan.',
            'address': 'Masukkan alamat lengkap perusahaan.',
            'phone_number': 'Masukkan nomor telepon perusahaan.',
            'email': 'Masukkan alamat email perusahaan.',
            'logo': 'Unggah logo perusahaan (opsional).',
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
        # fields = ['name', 'address', 'phone_number', 'email', 'logo']
        # widgets = {
        #     'name': forms.TextInput(attrs={'class': 'form-control'}),
        #     'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        #     'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control'}),
        #     'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        # }

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
        # fields = ['name', 'address', 'phone_number', 'email', 'logo']
        # widgets = {
        #     'name': forms.TextInput(attrs={'class': 'form-control'}),
        #     'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        #     'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control'}),
        #     'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        # }

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        exclude = ['created_at', 'updated_at']

        labels = {
            'name': 'Nama Part',
            'part_code': 'Kode Part',
            'jenis_part': 'Jenis Part',
            'description': 'Deskripsi Part',
            'quantity': 'Kuantitas',
            'unit_price': 'Harga Satuan',
            'vendor': 'Vendor',
        }

        help_texts = {
            'name': 'Masukkan nama part.',
            'part_code': 'Masukkan kode unik untuk part.',
            'jenis_part': 'Pilih jenis part dari daftar yang tersedia.',
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
            'jenis_part': {
                'required': 'Jenis part harus dipilih.',
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
        # fields = [
        #     'name','part_code','jenis_part',
        #     'description','quantity','unit_price','vendor'
        #     ]
        # widgets = {
        #     'name': forms.TextInput(attrs={'class': 'form-control'}),
        #     'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        #     'vendor': forms.Select(attrs={'class': 'form-control'}),
        #     'price': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        # }
