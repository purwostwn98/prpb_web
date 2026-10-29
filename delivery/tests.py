import datetime

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from rest_framework.test import APIClient

from master.models import Driver, Merek, Product, Spbu, Truck
from .forms import ShippingForm
from .models import Shipping, ShippingItem, ShippingTo


class ShippingAssignmentValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Merek.objects.create(nama='Hino', deskripsi='-')
        truck_defaults = dict(brand=brand, model='FM', year=2020, capacity=16000, current_odometer=0)
        cls.truck = Truck.objects.create(license_plate='AD 1 AA', **truck_defaults)
        cls.truck2 = Truck.objects.create(license_plate='AD 2 AA', **truck_defaults)
        cls.truck_maint = Truck.objects.create(license_plate='AD 3 AA', status='maintenance', **truck_defaults)

        def make_driver(username, license_number, active=True):
            user = User.objects.create_user(username, password='x', is_active=active)
            return Driver.objects.create(
                name=username, user=user, license_number=license_number,
                phone_number='0', years_old=30, address='-',
            )
        cls.driver = make_driver('budi', 'SIM1')
        cls.driver2 = make_driver('andi', 'SIM2')
        cls.driver_inactive = make_driver('cahyo', 'SIM3', active=False)

        cls.admin = User.objects.create_user('admin_test', password='pw')
        cls.spbu = Spbu.objects.create(code='44.571.01', name='SPBU Test')
        cls.product = Product.objects.create(name='Pertamax', description='-', price=1, stock=0)

    def form(self, **overrides):
        data = {
            'delivery_number': 'DO-NEW', 'order_date': '2026-10-28', 'status': 'draft',
            'truck': self.truck.pk, 'driver': self.driver.pk,
        }
        data.update(overrides)
        return ShippingForm(data)

    def make_shipping(self, number, status, truck, driver):
        return Shipping.objects.create(
            delivery_number=number, order_date=datetime.date(2026, 10, 28),
            status=status, truck=truck, driver=driver,
        )

    def test_truck_in_maintenance_is_rejected_for_open_shipping(self):
        form = self.form(truck=self.truck_maint.pk)
        self.assertFalse(form.is_valid())
        self.assertIn('truck', form.errors)

    def test_truck_in_maintenance_allowed_for_completed_shipping(self):
        self.assertTrue(self.form(truck=self.truck_maint.pk, status='completed').is_valid())

    def test_inactive_driver_is_rejected(self):
        form = self.form(driver=self.driver_inactive.pk)
        self.assertFalse(form.is_valid())
        self.assertIn('driver', form.errors)

    def test_truck_and_driver_cannot_run_two_shipments_at_once(self):
        self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        form = self.form(status='on_progress')
        self.assertFalse(form.is_valid())
        self.assertIn('DO-1', form.errors['truck'][0])
        self.assertIn('DO-1', form.errors['driver'][0])

    def test_multiple_pending_shipments_are_allowed(self):
        self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        self.assertTrue(self.form(status='pending').is_valid())

    def test_editing_running_shipment_does_not_conflict_with_itself(self):
        shipping = self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        data = {'delivery_number': 'DO-1', 'order_date': '2026-10-28', 'status': 'on_progress',
                'truck': self.truck.pk, 'driver': self.driver.pk, 'notes': 'edit'}
        self.assertTrue(ShippingForm(data, instance=shipping).is_valid())

    def test_update_view_shows_errors_instead_of_redirecting(self):
        shipping = self.make_shipping('DO-1', 'draft', self.truck, self.driver)
        self.client.force_login(self.admin)
        response = self.client.post(f'/delivery/update-shipping/{shipping.pk}/', {
            'delivery_number': 'DO-1', 'order_date': '2026-10-28', 'status': 'draft',
            'truck': self.truck_maint.pk, 'driver': self.driver.pk,
        })
        self.assertEqual(response.status_code, 200)
        shipping.refresh_from_db()
        self.assertEqual(shipping.truck, self.truck)

    def test_over_capacity_saves_with_warning(self):
        shipping = self.make_shipping('DO-1', 'draft', self.truck, self.driver)
        self.client.force_login(self.admin)
        response = self.client.post(f'/delivery/form-shippingto?shipping={shipping.pk}', {
            'shipping': shipping.pk, 'spbu': self.spbu.pk, 'estimated_distance_km': 10,
            'ol_number': 'OL-1', 'order_date': '2026-10-28',
            'items-TOTAL_FORMS': 1, 'items-INITIAL_FORMS': 0,
            'items-0-product': self.product.pk, 'items-0-quantity': 20000, 'items-0-unit_price': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ShippingItem.objects.filter(shippingto__shipping=shipping).count(), 1)
        warnings = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('melebihi kapasitas' in w for w in warnings))

    def destination_post(self, shipping, ol_number, **extra):
        data = {
            'shipping': shipping.pk, 'spbu': self.spbu.pk, 'estimated_distance_km': 10,
            'ol_number': ol_number, 'order_date': '2026-10-28',
            'items-TOTAL_FORMS': 1, 'items-INITIAL_FORMS': 0,
            'items-0-product': self.product.pk, 'items-0-quantity': 8000, 'items-0-unit_price': 1,
        }
        data.update(extra)
        return data

    def test_create_shipping_then_go_to_add_destination(self):
        self.client.force_login(self.admin)
        response = self.client.post('/delivery/form-shipping', {
            'delivery_number': 'DO-9', 'order_date': '2026-10-28', 'status': 'draft',
            'truck': self.truck.pk, 'driver': self.driver.pk, 'next_action': 'add_destination',
        })
        shipping = Shipping.objects.get(delivery_number='DO-9')
        self.assertRedirects(response, f'/delivery/form-shippingto?shipping={shipping.pk}')

    def test_save_and_add_another_destination(self):
        shipping = self.make_shipping('DO-1', 'draft', self.truck, self.driver)
        self.client.force_login(self.admin)
        url = f'/delivery/form-shippingto?shipping={shipping.pk}'
        response = self.client.post(url, self.destination_post(shipping, 'OL-1', next_action='add_another'))
        self.assertRedirects(response, url)

        page = self.client.get(url)
        self.assertEqual(len(page.context['existing_destinations']), 1)
        self.assertContains(page, 'OL-1')

        # the plain "Simpan" button still goes back to the shipping detail page
        response = self.client.post(url, self.destination_post(shipping, 'OL-2'))
        self.assertRedirects(response, f'/delivery/shipping/{shipping.pk}/')
        self.assertEqual(shipping.destinations.count(), 2)

    def test_within_capacity_has_no_warning(self):
        shipping = self.make_shipping('DO-1', 'draft', self.truck, self.driver)
        dest = ShippingTo.objects.create(
            shipping=shipping, spbu=self.spbu, estimated_distance_km=1,
            ol_number='OL-1', order_date=datetime.date(2026, 10, 28),
        )
        ShippingItem.objects.create(shippingto=dest, product=self.product, quantity=16000, unit_price=1)
        from .validators import shipping_capacity_warning
        self.assertIsNone(shipping_capacity_warning(shipping))

    def test_api_rejects_starting_second_running_shipment(self):
        self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        other = self.make_shipping('DO-2', 'pending', self.truck, self.driver2)
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.patch(f'/api/shipping/{other.pk}/', {'status': 'on_progress'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('truck', response.json())
        other.refresh_from_db()
        self.assertEqual(other.status, 'pending')

    def test_completed_shipping_updates_truck_odometer(self):
        shipping = self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.patch(f'/api/shipping/{shipping.pk}/', {'status': 'completed', 'odometer_end': 25000}, format='json')
        self.assertEqual(response.status_code, 200)
        self.truck.refresh_from_db()
        self.assertEqual((self.truck.current_odometer, self.truck.odometer_source), (25000, 'shipping'))

    def test_odometer_end_lower_than_truck_is_rejected(self):
        Truck.objects.filter(pk=self.truck.pk).update(current_odometer=30000)
        shipping = self.make_shipping('DO-1', 'on_progress', self.truck, self.driver)
        client = APIClient()
        client.force_authenticate(self.admin)
        response = client.patch(f'/api/shipping/{shipping.pk}/', {'status': 'completed', 'odometer_end': 25000}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('odometer_end', response.json())
        self.assertFalse(self.form(odometer_end=25000).is_valid())

    def test_shipping_list_shows_destinations_and_load(self):
        shipping = self.make_shipping('DO-1', 'draft', self.truck, self.driver)
        for ol, qty in (('OL-1', 8000), ('OL-2', 9000)):
            dest = ShippingTo.objects.create(
                shipping=shipping, spbu=self.spbu, estimated_distance_km=1, ol_number=ol,
                order_date=datetime.date(2026, 10, 28),
            )
            ShippingItem.objects.create(shippingto=dest, product=self.product, quantity=qty, unit_price=1)
        self.client.force_login(self.admin)
        row = self.client.get('/delivery/list-shipping').context['shippings'].get(pk=shipping.pk)
        self.assertEqual((row.destination_count, row.total_quantity), (2, 17000))
        response = self.client.get(f'/delivery/shipping/{shipping.pk}/')
        self.assertContains(response, 'Melebihi kapasitas')  # 17.000 L on a 16.000 L truck
