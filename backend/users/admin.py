# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id_user', 'login', 'nom', 'prenom', 'email', 'telephone', 'role', 'actif', 'is_staff', 'is_superuser')
    list_filter = ('role', 'actif', 'is_staff', 'is_superuser')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'login')
    ordering = ('-id_user',)

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom', 'email', 'telephone', 'date_naissance', 'role', 'actif')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
