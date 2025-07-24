from django.shortcuts import render, redirect, get_object_or_404 # type: ignore

# Create your views here.
from .models import Merek, Truck, Company, Vendor, Part
from .forms import MerekForm, TruckForm, CompanyForm, VendorForm, PartForm

def coba_template(request):
    return render(request, 'base.html')


# Views daftar data 
def merek_list(request):
    mereks = Merek.objects.all().order_by('-updated_at')
    data = {
        'page': ['master', 'merek'],
        'title': 'Daftar Merek'
    }   
    return render(request, 'master/merek_list.html', {'mereks': mereks, 'data': data})


def truck_list(request):
    trucks = Truck.objects.all().order_by('-updated_at')
    return render(request, 'master/truck_list.html', {'trucks': trucks})


def company_list(request):
    companies = Company.objects.all().order_by('-updated_at')
    return render(request, 'master/company_list.html', {'companies': companies})


def vendor_list(request):
    vendors = Vendor.objects.all().order_by('-updated_at')
    return render(request, 'master/vendor_list.html', {'vendors': vendors})


def part_list(request):
    parts = Part.objects.all().order_by('-updated_at')
    return render(request, 'master/part_list.html', {'parts': parts})



# Create views formulir
def create_Merek(request):
    context = {}
    form_merek = MerekForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_merek.is_valid():
            form_merek.save()
            return redirect('merek_list')  # Redirect to the list view after saving
    context['form_merek'] = form_merek
    return render(request, 'master/create_merek.html', context)


def create_Truck(request):
    context  ={}
    form_truck = TruckForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_truck.is_valid():
            form_truck.save()
            return redirect('truck_list')  # Redirect to the list view after saving
    context['form_truck'] = form_truck
    return render(request, 'master/create_truck.html', context)


def create_Company(request):
    context = {}
    form_company = CompanyForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':        
        if form_company.is_valid():
            form_company.save()
            return redirect('company_list')  # Redirect to the list view after saving
    context['form_company'] = form_company
    return render(request, 'master/create_company.html', context)
    

def create_Vendor(request):
    context = {}
    form_vendor = VendorForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_vendor.is_valid():
            form_vendor.save()
            return redirect('vendor_list')  # Redirect to the list view after saving
    context['form_vendor'] = form_vendor 
    return render(request, 'master/create_vendor.html', context)
    

def create_Part(request):
    context = {}
    form_part = PartForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_part.is_valid():
            form_part.save()
            return redirect('part_list')
    context['form_part'] = form_part 
    return render(request, 'master/create_part.html', context)
    

# Create views untuk update
def update_Merek(request, pk):
    merek = get_object_or_404(Merek, pk=pk)
    form_merek = MerekForm(request.POST or None, request.FILES or None, instance=merek)
    if request.method == 'POST':
        if form_merek.is_valid():
            form_merek.save()  # This will update the existing object, not create a new one
            return redirect('merek_list')
    context = {
        'form_merek': form_merek,
        'page_title': 'Update Merek',
    }
    return render(request, 'master/create_merek.html', context)



def update_Truck(request, pk):
    truck = get_object_or_404(Truck, pk=pk)

    data ={
        'license_plate': truck.license_plate,
        'brand': truck.brand,
        'model': truck.model,
        'year': truck.year,
        'capacity': truck.capacity,
        'current_odometer': truck.current_odometer,
        'status': truck.status,
        'acquisition_date': truck.acquisition_date,
        'engine_number': truck.engine_number,
        'chassis_number': truck.chassis_number,
        'created_at': truck.created_at,
        'updated_at': truck.updated_at,
        }

    form_truck = TruckForm(request.POST or None, initial=data, instance=truck)
    if request.method == 'POST':
        if form_truck.is_valid():
            form_truck.save()
        return redirect('truck_list')  # Redirect to the list view after saving
    context ={
        'form_truck': form_truck,
        'page_title': 'Update Truck',
    }
    return render(request, 'master/create_truck.html', context)


def update_Company(request, pk):
    company = get_object_or_404(Company, pk=pk)

    data = {
        'name': company.name,
        'address': company.address,
        'phone_number': company.phone_number,
        'email': company.email,
        'logo': company.logo,
        'created_at': company.created_at,
        'updated_at': company.updated_at,
    }
    form_company = CompanyForm(request.POST or None,initial=data, instance=company)
    if request.method == 'POST':
        if form_company.is_valid():
            form_company.save()
        return redirect('company_list')  # Redirect to the list view after saving
    
    context ={
        'form_company': form_company,
        'page_title': 'Update Company',
    }
    return render(request, 'master/create_company.html', context)


def update_Vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    data = {
        'name': vendor.name,
        'address': vendor.address,
        'phone_number': vendor.phone_number,
        'email': vendor.email,
        'logo': vendor.logo,
        'created_at': vendor.created_at,
        'updated_at': vendor.updated_at,
    }
    form_vendor = VendorForm(request.POST or None, initial=data, instance=vendor)
    if request.method == 'POST':
        if form_vendor.is_valid():
            form_vendor.save()
        return redirect('vendor_list')  # Redirect to the list view after saving
    context = {
        'form_vendor': form_vendor,
        'page_title': 'Update Vendor',
    }
    return render(request, 'master/create_vendor.html', context)


def update_Part(request, pk):
    part = get_object_or_404(Part, pk=pk)
    data = {
        'name': part.name,
        'part_code': part.part_code,
        'jenis_part': part.jenis_part,
        'description': part.description,
        'quantity': part.quantity,
        'unit_price': part.unit_price,
        'vendor': part.vendor,
        'created_at': part.created_at,
        'updated_at': part.updated_at,
    }
    form_part = PartForm(request.POST or None, initial=data, instance=part)
    if request.method == 'POST':
        if form_part.is_valid():
            form_part.save()
        return redirect('part_list')  # Redirect to the list view after saving
    
    context = {
        'form_part': form_part,
        'page_title': 'Update Part',
    }
    return render(request, 'master/create_part.html', context)



# Create views untuk delete
def delete_Merek(request, pk):
    merek = get_object_or_404(Merek, pk=pk)
    if request.method == 'POST':
        merek.delete()
    return redirect('merek_list')


def delete_Truck(request, pk):
    truck = get_object_or_404(Truck, pk=pk)
    if request.method == 'POST':
        truck.delete()
    return redirect('truck_list')

    
def delete_Company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
    return redirect('company_list')
    

def delete_Vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
    return redirect('vendor_list')


def delete_Part(request, pk):
    part = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        part.delete()
    return redirect('part_list')





# Full Form
# def create_form(request):
#     context = {}
#     merek_form = MerekForm(request.POST or None, request.FILES or None)
#     truck_form = TruckForm(request.POST or None, request.FILES or None)
#     company_form = CompanyForm(request.POST or None, request.FILES or None)
#     vendor_form = VendorForm(request.POST or None, request.FILES or None)
#     part_form = PartForm(request.POST or None, request.FILES or None)

#     forms = [merek_form, truck_form, company_form, vendor_form, part_form]

#     if request.method == 'POST':
#         if all(form.is_valid() for form in forms):
#             for form in forms:
#                 form.save()
#         # Always add forms to context so they are available in the template
#     context['merek_form'] = merek_form
#     context['truck_form'] = truck_form
#     context['company_form'] = company_form
#     context['vendor_form'] = vendor_form
#     context['part_form'] = part_form

#     return render(request, 'master/create.html', context)