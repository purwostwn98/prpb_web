# Browser tab titles for pages whose view does not pass a `title` in its context.
PAGE_TITLES = {
    'merek_list': 'Data Merek', 'create_Merek': 'Tambah Merek', 'update_Merek': 'Update Merek',
    'truck_list': 'Data Truck', 'create_Truck': 'Tambah Truck', 'update_Truck': 'Update Truck',
    'company_list': 'Data Perusahaan', 'create_Company': 'Tambah Perusahaan', 'update_Company': 'Update Perusahaan',
    'vendor_list': 'Data Vendor', 'create_Vendor': 'Tambah Vendor', 'update_Vendor': 'Update Vendor',
    'part_list': 'Data Part', 'create_Part': 'Tambah Part', 'update_Part': 'Update Part',
    'driver_list': 'Data Driver', 'create_Driver': 'Tambah Driver', 'update_Driver': 'Update Driver',
    'spbu_list': 'Data SPBU', 'create_Spbu': 'Tambah SPBU', 'update_Spbu': 'Update SPBU',
    'product_list': 'Data Produk', 'create_Product': 'Tambah Produk', 'update_Product': 'Update Produk',
    'user_list': 'Manajemen User', 'create_User': 'Tambah User', 'update_User': 'Update User',
}


def page_title(request):
    match = getattr(request, 'resolver_match', None)
    return {'default_page_title': PAGE_TITLES.get(match.url_name) if match else None}
