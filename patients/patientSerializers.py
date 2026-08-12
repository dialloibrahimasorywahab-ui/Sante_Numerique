from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            "idPatient",
            "idUtilisateur",
            "nom",
            "prenom",
            "dateNaissance",
            "sexe",
            "adresse",
            "telephone",
            "email",
            "groupeSanguin",
            "numeroSecuriteSociale",
            "personneAContacter",
            "dateInscription",
        ]

