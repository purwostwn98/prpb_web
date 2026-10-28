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
