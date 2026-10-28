"""
Per-component maintenance analytics shared by the web dashboard and the REST API.

A "replacement" of a component is a maintenance Record that has a RecordItem with
that component type and action 'replace'. MTTF, reliability and the next-service
prediction are always computed from the replacements of one component, so e.g.
oil changes never distort the fuel filter intervals.
"""
import numbers
from datetime import date, timedelta

from django.db.models import OuterRef, Subquery # type: ignore
from django.utils import timezone # type: ignore

import numpy as np # type: ignore
from reliability.Fitters import Fit_Everything # type: ignore

from master.models import ComponentType, Truck
from .models import Record, RecordItem

DEFAULT_COMPONENT_CODE = 'FILTER_SOLAR_ATAS'
IDEAL_ODOMETER = 10000  # KM between replacements considered ideal (OEE / MTTF %)
MIN_TTF_KM = 1000  # smaller odometer gaps are treated as duplicate entries, not a new interval
# on the same service date the higher odometer reading happened later
NEWEST_FIRST = ('-service_date', '-odometer_reading', '-id')


def get_component(code=None):
    """
    Resolve a ComponentType from its code, falling back to the default fuel filter
    and then to any active tracked component. Returns None if none exist.
    """
    if code:
        component = ComponentType.objects.filter(code=code).first()
        if component:
            return component
    return (
        ComponentType.objects.filter(code=DEFAULT_COMPONENT_CODE).first()
        or ComponentType.objects.filter(is_active=True, track_reliability=True).first()
    )


def tracked_components():
    return ComponentType.objects.filter(is_active=True, track_reliability=True).order_by('name')


def component_records(truck_id, component=None):
    """
    Records of a truck in which `component` was replaced. Without a component,
    every record of the truck is returned.
    """
    records = Record.objects.filter(truck_id=truck_id)
    if component is None:
        return records
    replaced = RecordItem.objects.filter(
        component_type=component, action=RecordItem.ACTION_REPLACE
    ).values('record_id')
    return records.filter(pk__in=replaced)


def time_to_failures(truck_id, component=None):
    """
    KM between consecutive replacements (sorted by odometer), skipping gaps
    of MIN_TTF_KM or less. Returns (ttf_list, labels).
    """
    odometers = list(
        component_records(truck_id, component)
        .filter(odometer_reading__gt=0)
        .order_by('odometer_reading')
        .values_list('odometer_reading', flat=True)
    )
    ttf, labels = [], []
    for i in range(len(odometers) - 1):
        gap = odometers[i + 1] - odometers[i]
        if gap > MIN_TTF_KM:
            ttf.append(gap)
            labels.append("Service " + str(i + 1) + " - " + str(i + 2))
    return ttf, labels


def reliability_summary(truck, component=None):
    """
    OEE, simple MTTF (mean of the intervals) and reliability shown on the truck dashboard.
    """
    records = component_records(truck.id, component)

    # last performance: the two highest distinct odometer readings
    top_odometers = list(
        records.filter(odometer_reading__isnull=False)
        .order_by('-odometer_reading')
        .values_list('odometer_reading', flat=True)
        .distinct()[:2]
    )
    max_record = top_odometers[0] if len(top_odometers) > 0 else 0
    second_max_record = top_odometers[1] if len(top_odometers) > 1 else 0
    availability = (max_record - second_max_record) / IDEAL_ODOMETER * 100 if max_record and second_max_record else 0
    performance = ((max_record - second_max_record) / IDEAL_ODOMETER) * 100 if max_record else 0
    quality = 100  # Assuming quality is always 100% for this example
    oee_value = (availability * performance * quality) / 10000 if availability and performance else 0
    if oee_value > 100:
        oee_value = 99.99

    ttf, _ = time_to_failures(truck.id, component)
    mttf = sum(ttf) / len(ttf) if ttf else 0
    persentase_mttf = mttf / IDEAL_ODOMETER * 100 if mttf else 0
    # an interval shorter than 8.000 KM counts as an early failure
    failures = sum(1 for gap in ttf if gap < 8000)
    reliability = (len(ttf) - failures) / len(ttf) * 100 if ttf else 0

    return {
        'oee_value': round(oee_value, 2),
        'mttf': round(mttf, 2),
        'persentase_mttf': round(persentase_mttf, 2),
        'reliability': round(reliability, 2),
        'jumlah_maintenance': records.filter(odometer_reading__gt=0).count(),
    }


def fitted_mttf(truck_id, component=None):
    """
    MTTF and reliability at IDEAL_ODOMETER from the best-fitting lifetime distribution.
    Falls back to the plain mean when there are too few intervals to fit, or when the
    best distribution has no defined mean.
    """
    ttf, labels = time_to_failures(truck_id, component)
    mttf, distribution_name, reliability_score = None, 'Unknown', 0
    if len(ttf) >= 2:
        try:
            best_dist = Fit_Everything(
                failures=ttf,
                print_results=False,
                show_histogram_plot=False,
                show_PP_plot=False,
                show_probability_plot=False,
                show_best_distribution_probability_plot=False,
            ).best_distribution
        except Exception as e:  # the fitter raises on degenerate data (e.g. identical intervals)
            print(f"Distribution fitting failed for truck {truck_id}: {e}")
            best_dist = None
        if best_dist is not None:
            distribution_name = best_dist.name
            mttf = best_dist.mean
            reliability_score = best_dist.SF(IDEAL_ODOMETER) * 100
    if not isinstance(mttf, numbers.Number) or not np.isfinite(mttf):
        mttf = float(np.mean(ttf)) if ttf else 0
    if not isinstance(reliability_score, numbers.Number) or not np.isfinite(reliability_score):
        reliability_score = 0
    return {
        'mttf': float(mttf),
        'distribution_name': distribution_name,
        'reliability_score': float(reliability_score),
        'labels': labels,
        'values': ttf,
    }


def _interval_stats(records):
    """KM/day differences between consecutive records (records sorted newest first)."""
    km, days = [], []
    for current_record, next_record in zip(records, records[1:]):
        if (current_record.odometer_reading or 0) > 0 and (next_record.odometer_reading or 0) > 0:
            km.append(current_record.odometer_reading - next_record.odometer_reading)
            days.append((current_record.service_date - next_record.service_date).days)
    return km, days


def next_service(truck, component=None, default_truck_age=1):
    """
    Features describing the replacement history plus the predicted next replacement.
    Fuel filters use the ML prediction API; other components use their configured interval.
    Returns None when the truck has no replacement of this component yet.
    """
    from core.utils import get_prediction_from_api

    records = list(component_records(truck.id, component).order_by(*NEWEST_FIRST))
    if not records:
        return None
    last_maintenance = records[0]

    if truck.year:
        truck_manufacture_date = date(int(truck.year), 1, 1)  # Assume the truck was made on Jan 1st of its year
        truck_age_at_service = (last_maintenance.service_date - truck_manufacture_date).days / 365.25
    else:
        truck_age_at_service = default_truck_age
    month_of_service = last_maintenance.service_date.month
    day_of_week = last_maintenance.service_date.weekday()

    # last interval: walk back until the gap is a real interval (> MIN_TTF_KM)
    last_ttf_km = 0
    last_ttf_days = 0
    for previous in records[1:]:
        last_ttf_km = (last_maintenance.odometer_reading or 0) - (previous.odometer_reading or 0)
        last_ttf_days = (last_maintenance.service_date - previous.service_date).days
        if last_ttf_km >= MIN_TTF_KM:
            break

    # rolling statistics over the last 6 records
    rolling_km, rolling_days = _interval_stats(records[:6])
    rolling_avg_km_3 = sum(rolling_km) / len(rolling_km) if rolling_km else 0
    rolling_std_km_3 = np.std(rolling_km) if rolling_km else 0
    rolling_avg_days_3 = sum(rolling_days) / len(rolling_days) if rolling_days else 0
    rolling_std_days_3 = np.std(rolling_days) if rolling_days else 0

    # cumulative averages over the whole history (oldest first, odometer not filtered)
    chronological = sorted(records, key=lambda r: r.service_date)
    pairs = list(zip(chronological, chronological[1:]))
    cumulative_avg_km = sum((b.odometer_reading or 0) - (a.odometer_reading or 0) for a, b in pairs) / len(pairs) if pairs else 0
    cumulative_avg_days = sum((b.service_date - a.service_date).days for a, b in pairs) / len(pairs) if pairs else 0
    cumulative_replacements = len(records)

    model = truck.model
    if component is None or component.has_ml_prediction:
        payload_data = {
            "truck_age_at_service": int(truck_age_at_service),
            "month_of_service": int(month_of_service),
            "day_of_week": int(day_of_week),
            "last_ttf_km": last_ttf_km,
            "last_ttf_days": int(last_ttf_days),
            "rolling_avg_km_3": rolling_avg_km_3,
            "rolling_std_km_3": rolling_std_km_3,
            "rolling_avg_days_3": rolling_avg_days_3,
            "rolling_std_days_3": rolling_std_days_3,
            "cumulative_replacements": int(cumulative_replacements),
            "cumulative_avg_km": cumulative_avg_km,
            "cumulative_avg_days": cumulative_avg_days,
            "model_" + str(model).upper(): 1
        }
        # get_prediction_from_api returns None if the prediction API is unreachable,
        # blocked (e.g. by Cloudflare), or returns a non-JSON/error response.
        predicted = get_prediction_from_api(payload_data)
        predicted_days = predicted.get('predicted_ttf_days') if predicted else None
        predicted_km = predicted.get('predicted_ttf_km') if predicted else None
        prediction_source = 'ml'
    else:
        predicted_days = component.interval_days
        predicted_km = component.interval_km
        prediction_source = 'interval'

    next_service_date = last_maintenance.service_date + timedelta(days=int(predicted_days) if predicted_days else 0)
    next_service_km = (last_maintenance.odometer_reading or 0) + predicted_km if predicted_km is not None else None

    return {
        'truck_data': {'id': truck.id, 'year': truck.year},
        'truck_age_at_service': round(truck_age_at_service, 2),
        'month_of_service': month_of_service,
        'last_ttf_km': last_ttf_km,
        'last_ttf_days': last_ttf_days,
        'rolling_avg_km_3': round(rolling_avg_km_3, 2),
        'rolling_avg_days_3': round(rolling_avg_days_3, 2),
        'count_commulative_service': cumulative_replacements,
        'commulative_km_average': cumulative_avg_km,
        'commulative_days_average': cumulative_avg_days,
        'truck_name': "model_" + str(model).upper(),
        'predicted_ttf_days': predicted_days if predicted_days else 0,
        'predicted_ttf_km': predicted_km if predicted_km else 0,
        'next_service_date': next_service_date.strftime('%Y-%m-%d'),
        'next_service_km': next_service_km if next_service_km else 0,
        'prediction_source': prediction_source,
        'component': {'code': component.code, 'name': component.name} if component else None,
    }


# --- Early warning: when is each truck due for its next replacement? ---

STATUS_OVERDUE = 'overdue'
STATUS_SOON = 'soon'
STATUS_OK = 'ok'
STATUS_NO_DATA = 'no_data'
STATUS_LABELS = {
    STATUS_OVERDUE: 'Terlambat',
    STATUS_SOON: 'Segera',
    STATUS_OK: 'Aman',
    STATUS_NO_DATA: 'Belum ada data',
}
STATUS_ORDER = [STATUS_OVERDUE, STATUS_SOON, STATUS_OK, STATUS_NO_DATA]
STALE_ODOMETER_DAYS = 7  # odometer older than this is flagged as possibly outdated


def due_status(component, truck, last_odometer, last_date, today=None):
    """
    Remaining KM/days until `component` must be replaced on `truck`, given its last
    replacement. Whichever limit (KM or days) comes first decides the status.
    """
    today = today or timezone.localdate()
    remaining_km = remaining_days = usage_pct = due_km = due_date = None
    if last_odometer is not None and component.interval_km:
        due_km = last_odometer + component.interval_km
        remaining_km = due_km - (truck.current_odometer or 0)
        usage_pct = ((truck.current_odometer or 0) - last_odometer) / component.interval_km * 100
    if last_date is not None and component.interval_days:
        due_date = last_date + timedelta(days=component.interval_days)
        remaining_days = (due_date - today).days

    if remaining_km is None and remaining_days is None:
        status = STATUS_NO_DATA
    elif (remaining_km is not None and remaining_km <= 0) or (remaining_days is not None and remaining_days <= 0):
        status = STATUS_OVERDUE
    elif (remaining_km is not None and component.warning_km and remaining_km < component.warning_km) or (
        remaining_days is not None and component.warning_days and remaining_days < component.warning_days
    ):
        status = STATUS_SOON
    else:
        status = STATUS_OK

    odometer_age_days = (timezone.now() - truck.odometer_updated_at).days if truck.odometer_updated_at else None
    return {
        'truck': truck,
        'last_odometer': last_odometer,
        'last_date': last_date,
        'due_km': due_km,
        'due_date': due_date,
        'remaining_km': remaining_km,
        'remaining_days': remaining_days,
        'usage_pct': round(usage_pct, 1) if usage_pct is not None else None,
        'status': status,
        'status_label': STATUS_LABELS[status],
        'odometer_age_days': odometer_age_days,
        'odometer_stale': odometer_age_days is None or odometer_age_days > STALE_ODOMETER_DAYS,
    }


def component_due_list(component, trucks=None):
    """
    Due status of `component` for every operating truck (inactive trucks are skipped),
    most urgent first.
    """
    trucks = trucks if trucks is not None else Truck.objects.exclude(status='inactive')
    last_replacement = component_records(OuterRef('pk'), component).order_by(*NEWEST_FIRST)
    trucks = trucks.select_related('brand').annotate(
        last_record_id=Subquery(last_replacement.values('pk')[:1]),
        last_odometer=Subquery(last_replacement.values('odometer_reading')[:1]),
        last_date=Subquery(last_replacement.values('service_date')[:1]),
    )
    today = timezone.localdate()
    rows = []
    for truck in trucks:
        row = due_status(component, truck, truck.last_odometer, truck.last_date, today)
        row['last_record_id'] = truck.last_record_id
        rows.append(row)
    rows.sort(key=lambda r: (
        STATUS_ORDER.index(r['status']),
        r['remaining_km'] if r['remaining_km'] is not None else float('inf'),
        r['remaining_days'] if r['remaining_days'] is not None else float('inf'),
        r['truck'].license_plate,
    ))
    return rows


def due_summary(rows):
    counts = {status: 0 for status in STATUS_ORDER}
    for row in rows:
        counts[row['status']] += 1
    return counts


def warning_components():
    """Active components that have a replacement interval, i.e. can be scheduled."""
    return ComponentType.objects.filter(is_active=True).exclude(interval_km__isnull=True, interval_days__isnull=True)


def get_warning_component(code=None):
    components = warning_components()
    return (
        (components.filter(code=code).first() if code else None)
        or components.filter(code='OLI_MESIN').first()
        or components.first()
    )
