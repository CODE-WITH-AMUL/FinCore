from django.urls import path
from .views import signin, signup, logout
from .profile import  userprofile
from .company import company_profile
urlpatterns = [
    # Authentication
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    
    # Profile section
    path('company/profile', company_profile, name='company_profile'),
    path('user/profile/', userprofile, name='userprofile'),
    
]