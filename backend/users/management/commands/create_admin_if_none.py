import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Crée un superadministrateur initial de manière idempotente (uniquement si aucun n'existe)."

    def handle(self, *args, **options):
        # Vérifier si au moins un superutilisateur existe déjà
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Un superadministrateur existe déjà. Aucune création nécessaire."))
            return

        login = os.environ.get("DJANGO_SUPERUSER_LOGIN") or os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@hopital.fr")
        nom = os.environ.get("DJANGO_SUPERUSER_NOM", "Admin")
        prenom = os.environ.get("DJANGO_SUPERUSER_PRENOM", "Principal")
        telephone = os.environ.get("DJANGO_SUPERUSER_TELEPHONE", "+224600000000")

        if not login or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Aucun superadministrateur trouvé, mais DJANGO_SUPERUSER_LOGIN ou DJANGO_SUPERUSER_PASSWORD n'est pas défini dans l'environnement. Ignoré."
                )
            )
            return

        user = User.objects.create_superuser(
            login=login,
            email=email,
            password=password,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            role=User.Role.ADMINISTRATEUR,
        )
        self.stdout.write(self.style.SUCCESS(f"Superadministrateur initial '{user.login}' créé avec succès."))

