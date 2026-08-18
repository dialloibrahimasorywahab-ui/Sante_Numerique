# pyrefly: ignore [missing-import]
# pyrefly: ignore [import-error]
from rest_framework import serializers
from .models import User


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "idUser",
            "nom",
            "prenom",
            "email",
            "telephone",
            "login",
            "motDePasseHash",
            "role",
            "derniereConnexion",
            "dateNaissance",
            "actif",
        ]

        extra_kwargs = {
            "motDePasseHash": {
                "write_only": True,
                "required": False,
            }
        }