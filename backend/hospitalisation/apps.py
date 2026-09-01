# pyrefly: ignore [missing-import]
from django.apps import AppConfig


class HospitalisationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospitalisation'
    verbose_name = 'Hospitalisation'
