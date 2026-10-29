import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase # type: ignore
from rest_framework.test import APIClient

from master.models import ComponentType, Merek, Part, Truck
from .analytics import component_records, fitted_mttf, get_component, next_service, reliability_summary, time_to_failures
from .forms import RecordItemFormSet
from .models import Record, RecordItem


class ComponentAnalyticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # seeded by migration master.0012
        cls.filter_atas = ComponentType.objects.get(code='FILTER_SOLAR_ATAS')
        # seeded by migration master.0015; give it a time interval too for these tests
        cls.oli = ComponentType.objects.get(code='OLI_MESIN')
        cls.oli.interval_km, cls.oli.interval_days = 20000, 180
        cls.oli.save()
        brand = Merek.objects.create(nama='Hino', deskripsi='-')
        cls.truck = Truck.objects.create(
            license_plate='AD 1 AA', brand=brand, model='FM', year=2020, capacity=16000, current_odometer=0,
        )
        cls.user = User.objects.create_user('tester', password='x')

        # fuel filter replaced every 10.000 KM, oil changed in between at 5.000 KM offsets
        for i, odo in enumerate([10000, 20000, 30000, 40000]):
            cls.add_record(odo, datetime.date(2025, 1, 1) + datetime.timedelta(days=60 * i), cls.filter_atas)
        for i, odo in enumerate([15000, 35000]):
            cls.add_record(odo, datetime.date(2025, 2, 1) + datetime.timedelta(days=120 * i), cls.oli, quantity=8)
        # topping up oil is not a replacement
        cls.add_record(37000, datetime.date(2025, 8, 1), cls.oli, action='top_up', quantity=1)

    @classmethod
    def add_record(cls, odometer, service_date, component, action='replace', quantity=1):
        record = Record.objects.create(
            truck=cls.truck, maintenance_type='service', booking_date=service_date, service_date=service_date,
            odometer_reading=odometer, service_location='-', technician_name='-', status='done',
        )
        RecordItem.objects.create(record=record, component_type=component, action=action, quantity=quantity)
        return record

    def test_records_are_filtered_per_component_and_replacement(self):
        self.assertEqual(component_records(self.truck.id, self.filter_atas).count(), 4)
        self.assertEqual(component_records(self.truck.id, self.oli).count(), 2)
        self.assertEqual(component_records(self.truck.id).count(), 7)

    def test_oil_changes_do_not_distort_fuel_filter_intervals(self):
        ttf, _ = time_to_failures(self.truck.id, self.filter_atas)
        self.assertEqual(ttf, [10000, 10000, 10000])
        summary = reliability_summary(self.truck, self.filter_atas)
        self.assertEqual(summary['mttf'], 10000)
        self.assertEqual(summary['reliability'], 100)
        self.assertEqual(summary['jumlah_maintenance'], 4)

    def test_fitted_mttf_needs_at_least_two_intervals(self):
        result = fitted_mttf(self.truck.id, self.oli)  # one interval only
        self.assertEqual(result['values'], [20000])
        self.assertEqual(result['distribution_name'], 'Unknown')
        self.assertEqual(result['mttf'], 20000)  # falls back to the plain mean

    @mock.patch('core.utils.get_prediction_from_api')
    def test_non_fuel_filter_component_uses_interval_without_ml(self, prediction):
        result = next_service(self.truck, self.oli)
        prediction.assert_not_called()
        self.assertEqual(result['prediction_source'], 'interval')
        self.assertEqual(result['predicted_ttf_km'], 20000)
        self.assertEqual(result['next_service_km'], 35000 + 20000)
        self.assertEqual(result['next_service_date'], '2025-11-28')  # 2025-06-01 + 180 days

    @mock.patch('core.utils.get_prediction_from_api', return_value={'predicted_ttf_days': 90, 'predicted_ttf_km': 9500})
    def test_fuel_filter_uses_ml_prediction(self, prediction):
        result = next_service(self.truck, self.filter_atas)
        payload = prediction.call_args.args[0]
        self.assertEqual(payload['cumulative_replacements'], 4)
        self.assertEqual(payload['last_ttf_km'], 10000)
        self.assertEqual(result['prediction_source'], 'ml')
        self.assertEqual(result['next_service_km'], 40000 + 9500)

    def test_no_history_returns_none(self):
        ban = ComponentType.objects.create(code='BAN', name='Ban', category='ban')
        self.assertIsNone(next_service(self.truck, ban))

    def test_get_component_defaults_to_fuel_filter(self):
        self.assertEqual(get_component(None), self.filter_atas)
        self.assertEqual(get_component('TIDAK_ADA'), self.filter_atas)
        self.assertEqual(get_component('OLI_MESIN'), self.oli)

    def test_dashboard_and_endpoints_follow_selected_component(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/maintenance/dashboard-truck?id={self.truck.id}&component=OLI_MESIN')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['component'], self.oli)
        self.assertEqual(response.context['jumlah_maintenance'], 2)

        history = self.client.get(f'/maintenance/dinamis/get-maintenance-history/{self.truck.id}/?component=OLI_MESIN').json()
        self.assertEqual(len(history['history']), 2)
        self.assertIn('Ganti Oli Mesin', history['history'][0]['components'])

        mttf = self.client.get(f'/maintenance/dinamis/get_mttf/{self.truck.id}/').json()
        self.assertEqual(mttf['distribution_data']['values'], [10000, 10000, 10000])

    def test_api_mttf_accepts_component(self):
        client = APIClient()
        client.force_authenticate(self.user)
        data = client.get(f'/api/truck-mttf/?truck_id={self.truck.id}&component=OLI_MESIN').json()
        self.assertEqual(data[0]['mttf']['values'], [20000])


class RecordItemFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filter_atas = ComponentType.objects.get(code='FILTER_SOLAR_ATAS')
        cls.oli = ComponentType.objects.get(code='OLI_MESIN')
        cls.oil_part = Part.objects.create(
            name='Rimula R4', part_code='SH-R4', component_type=cls.oli, description='-', quantity=0, unit_price=60000,
        )
        brand = Merek.objects.create(nama='Hino', deskripsi='-')
        cls.truck = Truck.objects.create(
            license_plate='AD 1 AA', brand=brand, model='FM', year=2020, capacity=16000, current_odometer=0,
        )
        cls.user = User.objects.create_user('tester', password='x')

    def record_post(self, rows, **extra):
        data = {
            'truck': self.truck.pk, 'maintenance_type': 'service', 'booking_date': '2026-10-28',
            'service_date': '2026-10-28', 'odometer_reading': 50000, 'service_location': 'Bengkel',
            'technician_name': 'Andi', 'cost': 0, 'status': 'done',
            'items-TOTAL_FORMS': len(rows), 'items-INITIAL_FORMS': 0,
        }
        for i, row in enumerate(rows):
            for key, value in row.items():
                data[f'items-{i}-{key}'] = value
        data.update(extra)
        return data

    def test_create_record_with_several_components(self):
        self.client.force_login(self.user)
        response = self.client.post('/maintenance/form-record', self.record_post([
            {'component_type': self.oli.pk, 'action': 'replace', 'part': self.oil_part.pk, 'quantity': '5.5'},
            {'component_type': self.filter_atas.pk, 'action': 'replace', 'quantity': 1},
        ]))
        self.assertRedirects(response, '/maintenance/list-record')
        record = Record.objects.get()
        oil = record.items.get(component_type=self.oli)
        self.assertEqual(str(oil.quantity), '5.50')
        self.assertEqual(oil.unit_price, 60000)  # copied from the part
        self.assertEqual(record.items.count(), 2)

    def test_empty_cost_is_filled_from_component_prices(self):
        self.client.force_login(self.user)
        self.client.post('/maintenance/form-record', self.record_post([
            {'component_type': self.oli.pk, 'action': 'replace', 'quantity': '5', 'unit_price': '60000'},
            {'component_type': self.filter_atas.pk, 'action': 'replace', 'quantity': 1, 'unit_price': '45000'},
        ], cost=''))
        self.assertEqual(Record.objects.get().cost, 345000)

    def test_record_list_filters_by_component(self):
        self.client.force_login(self.user)
        self.client.post('/maintenance/form-record', self.record_post([
            {'component_type': self.oli.pk, 'action': 'replace', 'quantity': '5'},
        ]))
        self.client.post('/maintenance/form-record', self.record_post([
            {'component_type': self.filter_atas.pk, 'action': 'replace', 'quantity': 1},
        ]))
        response = self.client.get('/maintenance/list-record?component=OLI_MESIN')
        self.assertEqual(response.context['page_obj'].paginator.count, 1)
        self.assertContains(response, 'Oli Mesin')

    def test_new_record_form_defaults_to_today(self):
        from django.utils import timezone
        self.client.force_login(self.user)
        form = self.client.get('/maintenance/form-record').context['form_record']
        self.assertEqual(form.initial['service_date'], timezone.localdate())

    def test_record_requires_at_least_one_component(self):
        self.client.force_login(self.user)
        response = self.client.post('/maintenance/form-record', self.record_post([]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Record.objects.exists())
        self.assertIn('minimal satu komponen', str(response.context['formset'].non_form_errors()))

    def test_part_must_match_component(self):
        formset = RecordItemFormSet(
            self.record_post([{'component_type': self.filter_atas.pk, 'action': 'replace', 'part': self.oil_part.pk, 'quantity': 1}]),
            instance=Record(), prefix='items',
        )
        self.assertFalse(formset.is_valid())
        self.assertIn('part', formset.forms[0].errors)

    def test_duplicate_component_action_rejected(self):
        row = {'component_type': self.oli.pk, 'action': 'replace', 'quantity': 1}
        formset = RecordItemFormSet(self.record_post([row, row]), instance=Record(), prefix='items')
        self.assertFalse(formset.is_valid())

    def test_update_with_invalid_items_shows_errors(self):
        record = Record.objects.create(
            truck=self.truck, maintenance_type='service', booking_date=datetime.date(2026, 10, 1),
            service_date=datetime.date(2026, 10, 1), service_location='-', technician_name='-',
        )
        item = RecordItem.objects.create(record=record, component_type=self.oli, quantity=1)
        self.client.force_login(self.user)
        data = self.record_post([], **{
            'items-TOTAL_FORMS': 1, 'items-INITIAL_FORMS': 1,
            'items-0-id': item.pk, 'items-0-component_type': self.oli.pk, 'items-0-action': 'replace',
            'items-0-quantity': 0, 'items-0-record': record.pk,
        })
        response = self.client.post(f'/maintenance/update-record/{record.pk}/', data)
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_component_in_use_cannot_be_deleted(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/master/delete-componenttype/{self.oli.pk}/', follow=True)
        self.assertTrue(ComponentType.objects.filter(pk=self.oli.pk).exists())
        self.assertContains(response, 'tidak dapat dihapus')


class EarlyWarningTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.oli = ComponentType.objects.get(code='OLI_MESIN')  # seeded: 10.000 KM, warning 2.000 KM
        cls.brand = Merek.objects.create(nama='Hino', deskripsi='-')
        cls.user = User.objects.create_user('tester', password='x')

    def make_truck(self, plate, odometer, status='active'):
        return Truck.objects.create(
            license_plate=plate, brand=self.brand, model='FM', year=2020, capacity=16000,
            current_odometer=odometer, status=status,
        )

    def change_oil(self, truck, odometer, service_date=datetime.date(2026, 10, 1), status='done'):
        record = Record.objects.create(
            truck=truck, maintenance_type='preventive', booking_date=service_date, service_date=service_date,
            odometer_reading=odometer, service_location='-', technician_name='-', status=status,
        )
        RecordItem.objects.create(record=record, component_type=self.oli, quantity=8)
        return record

    def rows_by_plate(self):
        from .analytics import component_due_list
        return {row['truck'].license_plate: row for row in component_due_list(self.oli)}

    def test_status_from_remaining_km(self):
        overdue, soon, ok, unknown = (self.make_truck(p, 0) for p in ('OVERDUE', 'SOON', 'OK', 'NODATA'))
        self.change_oil(overdue, 100000)
        self.change_oil(soon, 100000)
        self.change_oil(ok, 100000)
        Truck.objects.filter(pk=overdue.pk).update(current_odometer=110500)
        Truck.objects.filter(pk=soon.pk).update(current_odometer=108500)
        Truck.objects.filter(pk=ok.pk).update(current_odometer=101000)

        rows = self.rows_by_plate()
        self.assertEqual((rows['OVERDUE']['status'], rows['OVERDUE']['remaining_km']), ('overdue', -500))
        self.assertEqual((rows['SOON']['status'], rows['SOON']['remaining_km']), ('soon', 1500))
        self.assertEqual((rows['OK']['status'], rows['OK']['remaining_km']), ('ok', 9000))
        self.assertEqual(rows['NODATA']['status'], 'no_data')
        self.assertEqual(rows['SOON']['usage_pct'], 85.0)

    def test_exactly_2000_km_left_is_not_yet_a_warning(self):
        truck = self.make_truck('EDGE', 0)
        self.change_oil(truck, 100000)
        Truck.objects.filter(pk=truck.pk).update(current_odometer=108000)
        self.assertEqual(self.rows_by_plate()['EDGE']['status'], 'ok')

    def test_most_urgent_first_and_inactive_trucks_skipped(self):
        for plate, current in (('A', 105000), ('B', 111000), ('C', 109000)):
            truck = self.make_truck(plate, 0)
            self.change_oil(truck, 100000)
            Truck.objects.filter(pk=truck.pk).update(current_odometer=current)
        self.make_truck('PARKIR', 0, status='inactive')
        from .analytics import component_due_list
        self.assertEqual([r['truck'].license_plate for r in component_due_list(self.oli)], ['B', 'C', 'A'])

    def test_completed_maintenance_updates_truck_odometer(self):
        truck = self.make_truck('ODO', 50000)
        self.change_oil(truck, 60000)
        truck.refresh_from_db()
        self.assertEqual((truck.current_odometer, truck.odometer_source), (60000, 'maintenance'))
        # a draft booking is only a plan and must not move the odometer
        self.change_oil(truck, 70000, status='draft')
        truck.refresh_from_db()
        self.assertEqual(truck.current_odometer, 60000)

    def test_odometer_never_goes_backwards(self):
        from master.odometer import record_odometer
        truck = self.make_truck('ODO', 50000)
        self.assertFalse(record_odometer(truck, 40000, 'gps'))
        truck.refresh_from_db()
        self.assertEqual(truck.current_odometer, 50000)

    def test_manual_odometer_update(self):
        truck = self.make_truck('ODO', 50000)
        self.client.force_login(self.user)
        self.client.post(f'/maintenance/update-odometer/{truck.pk}/', {'odometer': '55.000'})
        truck.refresh_from_db()
        self.assertEqual((truck.current_odometer, truck.odometer_source), (55000, 'manual'))

        response = self.client.post(f'/maintenance/update-odometer/{truck.pk}/', {'odometer': '1000'}, follow=True)
        truck.refresh_from_db()
        self.assertEqual(truck.current_odometer, 55000)
        self.assertContains(response, 'lebih kecil dari KM terakhir')

    def test_early_warning_page_and_record_prefill(self):
        truck = self.make_truck('AD 9 ZZ', 0)
        self.change_oil(truck, 100000)
        Truck.objects.filter(pk=truck.pk).update(current_odometer=109000)
        self.client.force_login(self.user)

        response = self.client.get('/maintenance/early-warning?status=soon')
        self.assertEqual(response.context['component'], self.oli)
        self.assertEqual([r['truck'].pk for r in response.context['rows']], [truck.pk])
        self.assertContains(response, '1.000 KM')

        response = self.client.get(f'/maintenance/form-record?truck={truck.pk}&component=OLI_MESIN')
        self.assertEqual(response.context['form_record'].initial['odometer_reading'], 109000)
        self.assertEqual(response.context['formset'].forms[0].initial['component_type'], self.oli)

        response = self.client.get('/maintenance/dashboard')
        self.assertEqual(response.context['warning_counts']['soon'], 1)
