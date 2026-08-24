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

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            pwd = data.get("password") or data.get("motDePasse")
            if pwd and "motDePasseHash" not in data:
                data["motDePasseHash"] = pwd
        return super().to_internal_value(data)


    def validate(self, attrs):
        if not self.instance:
            errors = {}
            for field in ["nom", "prenom", "email", "telephone", "login"]:
                if not self.initial_data.get(field):
                    errors[field] = ["Ce champ est obligatoire."]
            if not self.initial_data.get("motDePasseHash") and not self.initial_data.get("motDePasse"):
                errors["motDePasse"] = ["Ce champ est obligatoire."]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs