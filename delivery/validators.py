from django.db.models import Sum # type: ignore

from .models import Shipping, ShippingItem

# Shipments that still need a truck and driver; completed/cancelled ones are history.
OPEN_STATUSES = ('draft', 'pending', 'on_progress')


def shipping_assignment_errors(truck, driver, status, exclude_pk=None):
    """
    Validate a truck/driver assignment for a shipment.
    Returns a dict of {field_name: message}; empty when the assignment is valid.

    Rules:
    - an open shipment may only use an active truck and an active driver account;
    - a truck or driver can only be on one shipment that is 'on_progress' at a time
      (several draft/pending shipments are allowed, e.g. multiple trips per day).
    """
    errors = {}
    if status not in OPEN_STATUSES:
        return errors

    if truck and truck.status != 'active':
        errors['truck'] = (
            f"Truck {truck.license_plate} sedang berstatus {truck.get_status_display()} "
            "dan tidak dapat ditugaskan."
        )
    if driver and driver.user_id and not driver.user.is_active:
        errors['driver'] = f"Akun driver {driver.name} tidak aktif dan tidak dapat ditugaskan."

    if status == 'on_progress':
        running = Shipping.objects.filter(status='on_progress').exclude(pk=exclude_pk)
        if truck and 'truck' not in errors:
            conflict = running.filter(truck=truck).first()
            if conflict:
                errors['truck'] = (
                    f"Truck {truck.license_plate} sedang menjalankan pengiriman "
                    f"{conflict.delivery_number} (On Progress)."
                )
        if driver and 'driver' not in errors:
            conflict = running.filter(driver=driver).first()
            if conflict:
                errors['driver'] = (
                    f"Driver {driver.name} sedang menjalankan pengiriman "
                    f"{conflict.delivery_number} (On Progress)."
                )
    return errors


def shipping_capacity_warning(shipping):
    """
    Return a warning message when the total quantity (liter) of all items in a shipment
    exceeds its truck's capacity, otherwise None.
    """
    if not shipping or not shipping.truck_id or shipping.status not in OPEN_STATUSES:
        return None
    total = ShippingItem.objects.filter(shippingto__shipping=shipping).aggregate(t=Sum('quantity'))['t'] or 0
    capacity = shipping.truck.capacity or 0
    if total > capacity:
        return (
            f"Total muatan pengiriman {shipping.delivery_number} ({total:,.0f} L) melebihi kapasitas "
            f"truck {shipping.truck.license_plate} ({capacity:,.0f} L). Periksa kembali muatan atau data kapasitas truck."
        ).replace(',', '.')
    return None
