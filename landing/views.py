from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.urls import reverse_lazy # type: ignore
from django.utils.http import url_has_allowed_host_and_scheme # type: ignore
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
            next_page = request.GET.get('next')
            if not next_page or not url_has_allowed_host_and_scheme(
                next_page, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                next_page = 'dashboard'
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'landing/index.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful!')
    return redirect('index')

# class DashboardView(TemplateView):
#     template_name = 'landing/dashboard.html'

# class LoginView(LoginView):
#     template_name = 'landing/login.html'
#     redirect_authenticated_user = True
