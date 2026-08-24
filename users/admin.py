from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('idUser', 'nom', 'prenom', 'email', 'telephone', 'login', 'role', 'actif', 'derniereConnexion')
    list_filter = ('role', 'actif')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'login')
    ordering = ('-idUser',)

