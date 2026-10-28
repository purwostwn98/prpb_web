from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan password'}),
    )
    password2 = forms.CharField(
        label='Konfirmasi Password',
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ulangi password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']

        labels = {
            'username': 'Username',
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'email': 'Email',
            'is_active': 'Akun Aktif',
            'is_staff': 'Akses Admin (Staff)',
        }

        error_messages = {
            'username': {
                'required': 'Username harus diisi.',
                'unique': 'Username ini sudah digunakan.',
                'max_length': 'Username tidak boleh lebih dari 150 karakter.',
            },
            'email': {'invalid': 'Masukkan alamat email yang valid.'},
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama depan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama belakang'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan email'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].help_text = 'Wajib diisi untuk user baru.'
        else:
            self.fields['password1'].help_text = 'Kosongkan jika tidak ingin mengubah password.'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Password dan konfirmasi password tidak sama.')
            else:
                try:
                    password_validation.validate_password(password1, self.instance)
                except ValidationError as e:
                    self.add_error('password1', e)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user
