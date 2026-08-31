from django.db import models
from django.contrib.auth.models import User


'''
This model class is use to login with the email in Singin Page instead of username.
'''


class UserLoginPrefernce(models.Model):
    username = None
    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name='User_login_preferences')
    email = models.EmailField(max_length=255, blank=True, null=True, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.user.email    