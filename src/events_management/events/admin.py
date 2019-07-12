from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from events.forms import CustomUserCreationForm, CustomUserChangeForm
from events.models import Account

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Account
    list_display = ['username',]

admin.site.register(Account, CustomUserAdmin)
