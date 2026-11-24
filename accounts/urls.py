from django.urls import path
from .views import (
    signin,
    signup,
    verify_signup_otp,
    logout,
    forget_password,
    verify_reset_otp,
    set_new_password,
)
from .profile import userprofile
from .company import company_profile


urlpatterns = [
    # Authentication
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('verify-signup-otp/', verify_signup_otp, name='verify_signup_otp'),
    path('logout/', logout, name='logout'),

    # Password reset flow
    path('forget-password/', forget_password, name='forget_password'),
    path('verify-reset-otp/', verify_reset_otp, name='verify_reset_otp'),
    path('set-new-password/', set_new_password, name='set_new_password'),

    # Profile section
    path('company/profile/', company_profile, name='company_profile'),
    path('user/profile/', userprofile, name='userprofile'),
]