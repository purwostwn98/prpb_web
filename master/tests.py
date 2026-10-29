import datetime

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase # type: ignore

from maintenance.models import Record
from .models import Driver, Merek, Truck, Vendor


class DeleteGuardTests(TestCase):
    """Master data that is still referenced elsewhere cannot be deleted."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('admin_test', password='x')
        cls.brand = Merek.objects.create(nama='Hino', deskripsi='-')
        cls.truck = Truck.objects.create(
            license_plate='AD 1 AA', brand=cls.brand, model='FM', year=2020, capacity=16000, current_odometer=0,
        )
        cls.vendor = Vendor.objects.create(name='Bengkel A', address='-', phone_number='0', email='a@example.com')
        Record.objects.create(
            truck=cls.truck, vendor=cls.vendor, maintenance_type='service', booking_date=datetime.date(2026, 1, 1),
            service_date=datetime.date(2026, 1, 1), service_location='-', technician_name='-',
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def messages_of(self, response):
        return [str(m) for m in get_messages(response.wsgi_request)]

    def test_brand_with_trucks_is_not_deleted(self):
        response = self.client.post(f'/master/delete-merek/{self.brand.pk}/')
        self.assertTrue(Merek.objects.filter(pk=self.brand.pk).exists())
        self.assertEqual(Record.objects.count(), 1)  # nothing cascaded
        self.assertIn('masih dipakai oleh 1 truck', self.messages_of(response)[0])

    def test_vendor_with_maintenance_records_is_not_deleted(self):
        response = self.client.post(f'/master/delete-vendor/{self.vendor.pk}/')
        self.assertTrue(Vendor.objects.filter(pk=self.vendor.pk).exists())
        self.assertIn('1 record maintenance', self.messages_of(response)[0])

    def test_unused_data_is_deleted(self):
        unused = Merek.objects.create(nama='Volvo', deskripsi='-')
        response = self.client.post(f'/master/delete-merek/{unused.pk}/')
        self.assertFalse(Merek.objects.filter(pk=unused.pk).exists())
        self.assertIn('berhasil dihapus', self.messages_of(response)[0])

    def test_list_shows_locked_delete_for_used_rows(self):
        Merek.objects.create(nama='Volvo', deskripsi='-')
        response = self.client.get('/master/list-merek')
        usage = {m.nama: m.usage for m in response.context['mereks']}
        self.assertEqual(usage, {'Hino': ['1 truck'], 'Volvo': []})
        self.assertContains(response, 'Tidak dapat dihapus: dipakai oleh 1 truck')
        self.assertContains(response, 'data-confirm="Hapus merek Volvo?"')

    def test_user_linked_to_driver_is_not_deleted(self):
        driver_user = User.objects.create_user('budi', password='x')
        Driver.objects.create(name='Budi', user=driver_user, license_number='SIM1', phone_number='0', years_old=30, address='-')
        self.client.post(f'/users/delete-user/{driver_user.pk}/')
        self.assertTrue(User.objects.filter(pk=driver_user.pk).exists())

        # admin log entries alone do not block deleting a user
        plain = User.objects.create_user('plain', password='x')
        self.client.post(f'/users/delete-user/{plain.pk}/')
        self.assertFalse(User.objects.filter(pk=plain.pk).exists())
