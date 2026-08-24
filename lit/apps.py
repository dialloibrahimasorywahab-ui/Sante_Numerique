# pyrefly: ignore [missing-import]
from django.apps import AppConfig


class LitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lit'

    def ready(self):
        import lit.signals  # noqa

