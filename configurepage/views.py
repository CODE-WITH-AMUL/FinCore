from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET




@never_cache
@require_GET
def index(request):
    '''Public Langin page Views.'''
    return render(request, 'landingpage/index.html')



@login_required
@never_cache
@require_GET

def home(request):
    """Authenticated application dashboard."""
    return render(request, 'pages/home.html')
