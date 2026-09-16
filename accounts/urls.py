from django.urls import path
from .views import signin, signup, logout
from .profile import company_profile, userprofile

urlpatterns = [
    # Authentication
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    
    # Profile section
    path('company/profile/<int:company_id>/', company_profile, name='company_profile'),
    path('profile/', userprofile, name='userprofile'),
    
]