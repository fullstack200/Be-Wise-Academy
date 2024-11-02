from django.contrib import admin

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from .models import *
from django.contrib.auth.admin import UserAdmin 
# Register your models here.

admin.site.register(Feedback)
admin.site.register(Enquiry)
admin.site.register(CustomUser)