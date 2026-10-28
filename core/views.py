from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.contrib.auth.models import User
from .forms import UserForm


def user_list(request):
    """
    View function to list all system users.
    """
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'total_count': users.count(),
        'active_count': User.objects.filter(is_active=True).count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'page': ['core', 'user'],
        'title': 'Daftar User',
    }
    return render(request, 'core/user_list.html', context)


def create_User(request):
    """
    View function to create a new system user.
    """
    context = {'page': ['core', 'user'], 'title': 'Tambah User'}
    form_user = UserForm(request.POST or None)
    if request.method == 'POST':
        if form_user.is_valid():
            form_user.save()
            return redirect('user_list')
    context['form_user'] = form_user
    return render(request, 'core/create_user.html', context)


def update_User(request, pk):
    """
    View function to update an existing system user.
    """
    user_obj = get_object_or_404(User, pk=pk)
    form_user = UserForm(request.POST or None, instance=user_obj)
    if request.method == 'POST':
        if form_user.is_valid():
            form_user.save()
            return redirect('user_list')
    context = {
        'form_user': form_user,
        'page_title': 'Update User',
        'page': ['core', 'user'],
        'title': 'Update User',
    }
    return render(request, 'core/create_user.html', context)


def delete_User(request, pk):
    """
    View function to delete a system user.
    """
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.delete()
    return redirect('user_list')
