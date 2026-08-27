from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase

from common.validators import (
    validate_phone_number,
    validate_date_not_in_future,
    validate_strict_positive,
    validate_blood_group,
    validate_numero_ordre,
    validate_nouveau_ne_metrics,
)
from users.models import User
from patients.models import Patient
from natalite.nataliteSerializers import NataliteSerializer
from mortalite.mortaliteSerializers import MortaliteSerializer
from frais_consultation.fraisSerializers import FraisConsultationSerializer


class UniversalValidatorsTests(TestCase):
    def test_validate_phone_number_valid(self):
        valid_numbers = [
            "+224622001122",
            "+33612345678",
            "0102030405",
            "0700000000",
            "+224 622 00 11 22",
            "01-02-03-04-05",
        ]
        for num in valid_numbers:
            self.assertEqual(validate_phone_number(num), num)

    def test_validate_phone_number_invalid(self):
        for num in ["123", "abc", "+12", "phone_number!"]:
            with self.assertRaises(ValidationError):
                validate_phone_number(num)

    def test_validate_date_not_in_future_valid(self):
        yesterday = date.today() - timedelta(days=1)
        today = date.today()
        self.assertEqual(validate_date_not_in_future(yesterday), yesterday)
        self.assertEqual(validate_date_not_in_future(today), today)
        self.assertEqual(validate_date_not_in_future("2020-01-01"), "2020-01-01")

    def test_validate_date_not_in_future_invalid(self):
        tomorrow = date.today() + timedelta(days=1)
        next_year = date.today() + timedelta(days=365)
        with self.assertRaises(ValidationError):
            validate_date_not_in_future(tomorrow)
        with self.assertRaises(ValidationError):
            validate_date_not_in_future(next_year)

    def test_validate_strict_positive_valid(self):
        self.assertEqual(validate_strict_positive(100), 100)
        self.assertEqual(validate_strict_positive(0.5), 0.5)
        self.assertEqual(validate_strict_positive("5000"), "5000")

    def test_validate_strict_positive_invalid(self):
        for val in [0, -1, -50.5, "0", "not_a_number"]:
            with self.assertRaises(ValidationError):
                validate_strict_positive(val)

    def test_validate_blood_group_valid(self):
        for bg in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "a+", "o-"]:
            self.assertTrue(validate_blood_group(bg))

    def test_validate_blood_group_invalid(self):
        for bg in ["C+", "XYZ", "A", "UNKNOWN"]:
            with self.assertRaises(ValidationError):
                validate_blood_group(bg)

    def test_validate_numero_ordre_valid(self):
        self.assertEqual(validate_numero_ordre("CNOM-12345"), "CNOM-12345")
        self.assertEqual(validate_numero_ordre("12345"), "12345")

    def test_validate_numero_ordre_invalid(self):
        with self.assertRaises(ValidationError):
            validate_numero_ordre("1")

    def test_validate_nouveau_ne_metrics_valid(self):
        validate_nouveau_ne_metrics(poids=3.5, taille=50.0)
        validate_nouveau_ne_metrics(poids=0.5, taille=25.0)

    def test_validate_nouveau_ne_metrics_invalid(self):
        with self.assertRaises(ValidationError):
            validate_nouveau_ne_metrics(poids=15.0, taille=50.0)
        with self.assertRaises(ValidationError):
            validate_nouveau_ne_metrics(poids=3.5, taille=10.0)


class SerializersCrossValidationTests(TestCase):
    def setUp(self):
        self.user_male = User.objects.create(
            nom="Diallo",
            prenom="Amadou",
            email="amadou@test.com",
            telephone="+224622000001",
            login="amadou_d",
            motDePasseHash="hash",
            role=User.Role.PATIENT,
        )
        self.patient_male = Patient.objects.create(
            idUtilisateur=self.user_male,
            dateNaissance="1990-05-15",
            sexe=Patient.Sexe.MASCULIN,
            dateInscription="2026-01-01",
        )

        self.user_female = User.objects.create(
            nom="Bah",
            prenom="Fatoumata",
            email="fatou@test.com",
            telephone="+224622000002",
            login="fatou_b",
            motDePasseHash="hash",
            role=User.Role.PATIENT,
        )
        self.patient_female = Patient.objects.create(
            idUtilisateur=self.user_female,
            dateNaissance="1995-08-20",
            sexe=Patient.Sexe.FEMININ,
            dateInscription="2026-01-01",
        )

    def test_natalite_serializer_male_mother_rejected(self):
        payload = {
            "id_patient": self.patient_male.idPatient,
            "nom_nouveau_ne": "Diallo",
            "prenom_nouveau_ne": "Ousmane",
            "date_naissance": str(date.today()),
            "heure_naissance": "10:00:00",
            "sexe": "M",
            "poids": 3.2,
            "taille": 50.0,
        }
        serializer = NataliteSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("id_patient", serializer.errors)

    def test_natalite_serializer_female_mother_accepted(self):
        payload = {
            "id_patient": self.patient_female.idPatient,
            "nom_nouveau_ne": "Bah",
            "prenom_nouveau_ne": "Mariama",
            "date_naissance": str(date.today()),
            "heure_naissance": "10:00:00",
            "sexe": "F",
            "poids": 3.4,
            "taille": 51.0,
        }
        serializer = NataliteSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_mortalite_serializer_death_before_birth_rejected(self):
        payload = {
            "id_patient": self.patient_male.idPatient,
            "date_deces": "1980-01-01",  # Born in 1990!
            "heure_deces": "12:00:00",
            "cause_deces": "Arret cardiaque",
        }
        serializer = MortaliteSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("date_deces", serializer.errors)

    def test_frais_consultation_serializer_negative_amount_rejected(self):
        payload = {
            "montant": -5000.0,
            "description": "Consultation",
        }
        serializer = FraisConsultationSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("montant", serializer.errors)
