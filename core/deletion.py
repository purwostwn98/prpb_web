"""
Block deleting master data that is still referenced elsewhere.

Several foreign keys use on_delete=CASCADE (e.g. deleting a brand would delete its
trucks and all their maintenance records). Until the models are changed, the views
refuse such deletes: an object can only be deleted when no other row points to it.

The references are read from the model's reverse relations, so a relation added
later is checked automatically.
"""
from django.contrib import messages # type: ignore
from django.db.models import Count # type: ignore

# Indonesian names for the tables that can reference master data.
USAGE_LABELS = {
    'master.Truck': 'truck',
    'master.Part': 'part',
    'master.Driver': 'data driver',
    'maintenance.Record': 'record maintenance',
    'maintenance.RecordItem': 'pekerjaan maintenance',
    'maintenance.TruckDeviceModel': 'perangkat IoT',
    'delivery.Shipping': 'pengiriman',
    'delivery.ShippingTo': 'tujuan pengiriman',
    'delivery.ShippingItem': 'item pengiriman',
}


def _relations(model, only=None):
    """Reverse relations (FK and M2M) pointing at `model`, optionally limited to some models."""
    relations = []
    for rel in model._meta.related_objects:
        label = rel.related_model._meta.label
        if only is not None and label not in only:
            continue
        relations.append(rel)
    return relations


def _label(rel):
    label = rel.related_model._meta.label
    return USAGE_LABELS.get(label, str(rel.related_model._meta.verbose_name))


def usage_of(obj, only=None):
    """e.g. ['120 truck', '3 pengiriman'] for the rows still referencing `obj`."""
    usage = []
    for rel in _relations(type(obj), only):
        count = getattr(obj, rel.get_accessor_name()).count()
        if count:
            usage.append(f"{count} {_label(rel)}")
    return usage


def with_usage(queryset, only=None):
    """
    Evaluate `queryset` and set `obj.usage` (list like usage_of) on every object,
    counting all references with annotations instead of one query per row.
    """
    relations = _relations(queryset.model, only)
    annotations = {f'_usage_{i}': Count(rel.name, distinct=True) for i, rel in enumerate(relations)}
    objects = list(queryset.annotate(**annotations))
    for obj in objects:
        obj.usage = [
            f"{getattr(obj, f'_usage_{i}')} {_label(rel)}"
            for i, rel in enumerate(relations)
            if getattr(obj, f'_usage_{i}')
        ]
    return objects


def delete_if_unused(request, obj, name, only=None):
    """
    Delete `obj` unless something still references it; report the outcome as a message.
    Returns True when the object was deleted.
    """
    usage = usage_of(obj, only)
    if usage:
        messages.error(
            request,
            f"{name} tidak dapat dihapus karena masih dipakai oleh {', '.join(usage)}. "
            "Hapus atau pindahkan data tersebut terlebih dahulu.",
        )
        return False
    obj.delete()
    messages.success(request, f"{name} berhasil dihapus.")
    return True
