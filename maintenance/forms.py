from django import forms
from django.db.models import Q
from master.models import ComponentType, Part
from .models import Record, RecordItem, TruckDeviceModel


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
            'cost': 'Biaya Total',
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
            'truck': forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Cari...'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan pembacaan odometer'}),
            'vendor': forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Cari...'}),
            'service_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan lokasi service'}),
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama teknisi'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Otomatis dari total komponen'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Masukkan deskripsi'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cost'].required = False
        if not self.instance.pk:
            self.initial['cost'] = None  # empty, so the component total is used unless a cost is typed

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        # empty cost means "use the total of the component prices" (filled in by the view)
        self.cost_from_items = cost is None
        return cost if cost is not None else 0


class RecordItemForm(forms.ModelForm):
    class Meta:
        model = RecordItem
        fields = ['component_type', 'action', 'part', 'quantity', 'unit_price', 'notes']

        labels = {
            'component_type': 'Komponen',
            'action': 'Tindakan',
            'part': 'Part',
            'quantity': 'Kuantitas',
            'unit_price': 'Harga Satuan',
            'notes': 'Catatan',
        }

        error_messages = {
            'component_type': {'required': 'Komponen harus dipilih.'},
            'quantity': {'required': 'Kuantitas harus diisi.', 'invalid': 'Masukkan angka yang valid.'},
        }

        widgets = {
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'action': forms.Select(attrs={'class': 'form-select'}),
            'part': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Dari part'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opsional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # inactive component types stay selectable on rows that already use them
        current = self.instance.component_type_id if self.instance.pk else None
        self.fields['component_type'].queryset = ComponentType.objects.filter(
            Q(is_active=True) | Q(pk=current)
        ).order_by('name')
        self.fields['part'].queryset = Part.objects.select_related('component_type').order_by('name')
        self.fields['part'].required = False
        self.fields['part'].empty_label = '- Tanpa part / tidak terdaftar -'
        self.fields['part'].label_from_instance = lambda p: f"{p.name} ({p.part_code}) - {p.component_type}"
        if not self.instance.pk:
            # no meaningful default: 1 fits a filter (pcs) but not engine oil (liter); the page JS fills pcs
            self.fields['quantity'].initial = None

    def clean(self):
        cleaned_data = super().clean()
        component_type = cleaned_data.get('component_type')
        part = cleaned_data.get('part')
        if part and component_type and part.component_type_id != component_type.pk:
            self.add_error('part', f"Part ini untuk {part.component_type}, bukan {component_type}.")
        quantity = cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', 'Kuantitas harus lebih dari 0.')
        # default to the catalogue price; the stored price is a snapshot at transaction time
        if part and cleaned_data.get('unit_price') is None:
            cleaned_data['unit_price'] = part.unit_price
        return cleaned_data


class BaseRecordItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        rows = [
            f.cleaned_data for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get('DELETE')
        ]
        if not rows:
            raise forms.ValidationError('Isi minimal satu komponen yang dikerjakan.')
        seen = set()
        for row in rows:
            key = (row['component_type'].pk, row['action'])
            if key in seen:
                raise forms.ValidationError(
                    f"{row['component_type']} dengan tindakan yang sama diisi lebih dari sekali."
                )
            seen.add(key)


RecordItemFormSet = forms.inlineformset_factory(
    Record,
    RecordItem,
    form=RecordItemForm,
    formset=BaseRecordItemFormSet,
    extra=1,
    can_delete=True,
)


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
