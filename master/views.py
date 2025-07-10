from django.shortcuts import render # type: ignore

# Create your views here.
from .models import Merek

def merek_list(request):
    mereks = Merek.objects.all().order_by('-updated_at')
    return render(request, 'master/merek_list.html', {'mereks': mereks})

def coba_template(request):
    return render(request, 'base.html')
