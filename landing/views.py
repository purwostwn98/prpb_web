from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.urls import reverse_lazy # type: ignore
from django.views.generic import TemplateView # type: ignore
from django.contrib.auth.views import LoginView, LogoutView # type: ignore


# Create your views here.
def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'landing/index.html')
