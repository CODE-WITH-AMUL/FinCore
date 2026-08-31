
'''
Django Accounts / Views.py Bussiness logic written
'''
#---------------------[IMPORTS]---------------------#
from django.shortcuts import render
from django.contrib.auth import login as user_login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import UserLoginPrefernce
from django.db import transaction
import logging
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import logout as user_logout
# from django.sh
#---------------------[LOGIN VIEW]---------------------#
'''
This function is used to signup the user with email and password.
'''
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    try:
        if request.method == "POST":
            email = request.POST.get('email').strip().lower()
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                user_login(request, user)
                '''
                Lets add the Session request
                '''
                
                request.session.set_expiry(60 * 60 * 24 * 30) # for 1 month
                messages.success(request, 'Login successful.')
                
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'authentication/login.html')


#-----------------------[REGISTER ACCOUNT VIEW]-----------------------#
'''
This fucntion is used to register the user with email and password.
'''
logger = logging.getLogger(__name__)
def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name' , '').strip()
        last_name = request.POST.get('last_name' , '').strip()
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        
        if not first_name or not last_name or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return redirect('signup')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('signup')
        
        '''
        We will use the transaction to make sure that the user is created successfully and if not then we will rollback the transaction.
        '''
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,  # Use email as username
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                UserLoginPrefernce.objects.create(user=user, email=email)
                messages.success(request, 'Account created successfully. Please login.')
                return redirect('signin')
        except Exception as e:
            # 6. Log the error securely instead of exposing it to the user
            logger.error(f"Error creating user account: {str(e)}", exc_info=True)
            messages.error(
                request, "An error occurred while creating your account. Please try again later."
            )
            return render(request, "authentication/signup.html")

    return render(request, "authentication/signup.html")


#-----------------------[LOGOUT VIEW]-----------------------#
@login_required()
def logout(request):
    user_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('signin')