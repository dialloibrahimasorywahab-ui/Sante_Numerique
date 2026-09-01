# pyrefly: ignore [missing-import]
from django.apps import AppConfig


class OrdonnanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ordonnance'
    verbose_name = 'Ordonnance'
