from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import Shipping, ShippingTo
from .forms import ShippingForm


def shipping_list(request):
    """
    View function to list all shipping / fleet assignments (driver + truck).
    """
    shippings = Shipping.objects.select_related('driver', 'truck').order_by('-order_date', '-id')

    status_filter = request.GET.getlist('status')
    if status_filter:
        shippings = shippings.filter(status__in=status_filter)

    total_count = Shipping.objects.count()
    active_count = Shipping.objects.filter(status__in=['pending', 'on_progress']).count()
    unassigned_count = Shipping.objects.filter(driver__isnull=True).count() + Shipping.objects.filter(truck__isnull=True).count()
    context = {
        'shippings': shippings,
        'status_filter': status_filter,
        'status_choices': Shipping.STATUS_CHOICES,
        'total_count': total_count,
        'active_count': active_count,
        'unassigned_count': unassigned_count,
        'page': ['delivery', 'shipping'],
        'title': 'Daftar Pengiriman',
    }
    return render(request, 'delivery/shipping_list.html', context)


def shipping_detail(request, pk):
    """
    View function to show shipping detail: assignment info, destinations, and items per destination.
    """
    shipping = get_object_or_404(Shipping.objects.select_related('driver', 'truck'), pk=pk)
    destinations = (
        ShippingTo.objects.filter(shipping=shipping)
        .select_related('spbu')
        .prefetch_related('items__product')
    )
    context = {
        'shipping': shipping,
        'destinations': destinations,
        'page': ['delivery', 'shipping'],
        'title': 'Detail Pengiriman',
    }
    return render(request, 'delivery/shipping_detail.html', context)


def create_Shipping(request):
    """
    View function to create a new shipping / fleet assignment.
    """
    context = {'page': ['delivery', 'shipping'], 'title': 'Tambah Pengiriman'}
    form_shipping = ShippingForm(request.POST or None)
    if request.method == 'POST':
        if form_shipping.is_valid():
            form_shipping.save()
            return redirect('shipping_list')
    context['form_shipping'] = form_shipping
    return render(request, 'delivery/create_shipping.html', context)


def update_Shipping(request, pk):
    """
    View function to update an existing shipping / fleet assignment.
    """
    shipping = get_object_or_404(Shipping, pk=pk)
    form_shipping = ShippingForm(request.POST or None, instance=shipping)
    if request.method == 'POST':
        if form_shipping.is_valid():
            form_shipping.save()
        return redirect('shipping_list')
    context = {
        'form_shipping': form_shipping,
        'page_title': 'Update Pengiriman',
        'page': ['delivery', 'shipping'],
        'title': 'Update Pengiriman',
    }
    return render(request, 'delivery/create_shipping.html', context)


def delete_Shipping(request, pk):
    """
    View function to delete a shipping / fleet assignment.
    """
    shipping = get_object_or_404(Shipping, pk=pk)
    if request.method == 'POST':
        shipping.delete()
    return redirect('shipping_list')
