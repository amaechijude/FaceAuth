from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

def register_user(request):
    pass

def login_user(request):
    pass

@login_required
def index_page(request):
    return render(request, 'index.html')
