from django import template # type: ignore

register = template.Library()


@register.filter
def ribuan(value):
    """Format a number with Indonesian thousand separators: 12500 -> '12.500'."""
    if value is None or value == '':
        return '-'
    try:
        return f"{int(round(float(value))):,}".replace(',', '.')
    except (TypeError, ValueError):
        return value


@register.filter
def rupiah(value):
    """Format an amount as Indonesian Rupiah: 200000000 -> 'Rp 200.000.000'."""
    if value is None or value == '':
        return '-'
    try:
        return 'Rp ' + f"{int(round(float(value))):,}".replace(',', '.')
    except (TypeError, ValueError):
        return value


# One meaning per colour across the app: green = done/OK, amber = needs attention or
# in progress, red = late/cancelled, grey = not started / no data.
STATUS_BADGE = {
    'success': ('done', 'completed', 'approved', 'active', 'ok'),
    'warning text-dark': ('pending', 'on_progress', 'in_progress', 'requested', 'awaiting_approval', 'soon', 'maintenance'),
    'danger': ('cancelled', 'rejected', 'inactive', 'overdue'),
}


@register.filter
def status_badge(status):
    """Badge classes for a status key, e.g. <span class="badge {{ s|status_badge }}">."""
    for colour, statuses in STATUS_BADGE.items():
        if status in statuses:
            return 'bg-' + colour
    return 'bg-light text-muted border'  # draft, no_data, unknown
