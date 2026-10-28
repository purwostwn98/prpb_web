"""
Single entry point for updating a truck's current odometer.

Every source (maintenance records, driver input when a delivery is completed,
manual admin input, and later GPS) goes through record_odometer(), so the
"odometer never goes backwards" rule is enforced in one place.
"""
import datetime

from django.utils import timezone # type: ignore

from .models import Truck


def record_odometer(truck, reading, source, when=None):
    """
    Store `reading` as the truck's current odometer if it is not lower than the
    stored value. `when` may be a date or datetime (defaults to now).
    Returns True when the truck was updated.
    """
    if truck is None or reading is None:
        return False
    if isinstance(when, datetime.date) and not isinstance(when, datetime.datetime):
        # a date only says which day; never claim a time later than now
        when = min(timezone.make_aware(datetime.datetime.combine(when, datetime.time.max)), timezone.now())
    when = when or timezone.now()

    # conditional UPDATE so two concurrent readings cannot move the odometer backwards
    updated = Truck.objects.filter(pk=truck.pk, current_odometer__lte=reading).update(
        current_odometer=reading, odometer_updated_at=when, odometer_source=source,
    )
    if updated:
        truck.current_odometer = reading
        truck.odometer_updated_at = when
        truck.odometer_source = source
    return bool(updated)


def odometer_error(truck, reading):
    """Validation message when `reading` is lower than the truck's known odometer, else None."""
    if truck is None or reading is None or reading >= (truck.current_odometer or 0):
        return None
    return (
        f"KM {reading:,} lebih kecil dari KM terakhir truck {truck.license_plate} "
        f"({truck.current_odometer:,})."
    ).replace(',', '.')
