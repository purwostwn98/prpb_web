from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count, Sum

# Create your views here.
from .models import Shipping, ShippingTo
from .forms import ShippingForm, ShippingToForm, ShippingItemFormSet
from .validators import shipping_capacity_warning


def warn_if_over_capacity(request, shipping):
    """
    Capacity is only a warning for now (truck capacity data is still being cleaned up),
    so the save goes through and the user is notified.
    """
    warning = shipping_capacity_warning(shipping)
    if warning:
        messages.warning(request, warning)


def shipping_list(request):
    """
    View function to list all shipping / fleet assignments (driver + truck).
    """
    shippings = (
        Shipping.objects.select_related('driver', 'truck')
        .annotate(
            destination_count=Count('destinations', distinct=True),
            total_quantity=Sum('destinations__items__quantity'),
        )
        .order_by('-order_date', '-id')
    )

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
    shipping = get_object_or_404(
        Shipping.objects.select_related('driver', 'truck').annotate(total_quantity=Sum('destinations__items__quantity')),
        pk=pk,
    )
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
            shipping = form_shipping.save()
            warn_if_over_capacity(request, shipping)
            if request.POST.get('next_action') == 'add_destination':
                messages.success(request, f"Pengiriman {shipping.delivery_number} disimpan. Silakan tambahkan SPBU tujuan.")
                return redirect(f"{reverse('create_ShippingTo')}?shipping={shipping.pk}")
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
            warn_if_over_capacity(request, form_shipping.save())
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


# Manajemen Pengiriman ke SPBU (ShippingTo)

def shippingto_list(request):
    """
    View function to list all SPBU delivery destinations across all shipments.
    """
    destinations = (
        ShippingTo.objects.select_related('shipping', 'spbu')
        .prefetch_related('items')
        .order_by('-order_date', '-id')
    )
    context = {
        'destinations': destinations,
        'total_count': destinations.count(),
        'page': ['delivery', 'shippingto'],
        'title': 'Daftar Pengiriman ke SPBU',
    }
    return render(request, 'delivery/shippingto_list.html', context)


def create_ShippingTo(request):
    """
    View function to add a new SPBU delivery destination to a shipment.
    If a `shipping` id is passed (e.g. from the shipping detail page), the
    shipping field is pre-selected and the user is returned there after saving.
    """
    shipping_id = request.GET.get('shipping') or request.POST.get('shipping')
    initial = {'shipping': shipping_id} if shipping_id else None
    back_url = reverse('shipping_detail', args=[shipping_id]) if shipping_id else reverse('shippingto_list')

    context = {
        'page': ['delivery', 'shippingto'],
        'title': 'Tambah Pengiriman ke SPBU',
        'back_url': back_url,
    }
    form_shippingto = ShippingToForm(request.POST or None, initial=initial)
    formset = ShippingItemFormSet(request.POST or None, instance=ShippingTo(), prefix='items')
    if request.method == 'POST':
        if form_shippingto.is_valid() and formset.is_valid():
            destination = form_shippingto.save()
            formset.instance = destination
            formset.save()
            warn_if_over_capacity(request, destination.shipping)
            if request.POST.get('next_action') == 'add_another':
                count = destination.shipping.destinations.count()
                messages.success(
                    request,
                    f"SPBU {destination.spbu.name or destination.spbu.code} ditambahkan ke pengiriman "
                    f"{destination.shipping.delivery_number} ({count} tujuan). Silakan isi SPBU berikutnya.",
                )
                return redirect(f"{reverse('create_ShippingTo')}?shipping={destination.shipping_id}")
            if shipping_id:
                return redirect('shipping_detail', pk=destination.shipping_id)
            return redirect('shippingto_list')
    context['form_shippingto'] = form_shippingto
    context['formset'] = formset
    if shipping_id and str(shipping_id).isdigit():
        context['existing_destinations'] = (
            ShippingTo.objects.filter(shipping_id=shipping_id)
            .select_related('spbu')
            .prefetch_related('items')
        )
    return render(request, 'delivery/create_shippingto.html', context)


def update_ShippingTo(request, pk):
    """
    View function to update an existing SPBU delivery destination and its products.
    """
    destination = get_object_or_404(ShippingTo, pk=pk)
    form_shippingto = ShippingToForm(request.POST or None, instance=destination)
    formset = ShippingItemFormSet(request.POST or None, instance=destination, prefix='items')
    if request.method == 'POST':
        if form_shippingto.is_valid() and formset.is_valid():
            destination = form_shippingto.save()
            formset.save()
            warn_if_over_capacity(request, destination.shipping)
            return redirect('shippingto_list')
    context = {
        'form_shippingto': form_shippingto,
        'formset': formset,
        'page_title': 'Update Pengiriman ke SPBU',
        'page': ['delivery', 'shippingto'],
        'title': 'Update Pengiriman ke SPBU',
    }
    return render(request, 'delivery/create_shippingto.html', context)


def delete_ShippingTo(request, pk):
    """
    View function to delete an SPBU delivery destination.
    """
    destination = get_object_or_404(ShippingTo, pk=pk)
    if request.method == 'POST':
        destination.delete()
    return redirect('shippingto_list')
