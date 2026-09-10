from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from patients.models import Patient
from medecin.models import Medecin
from consultation.models import Consultation
from ordonnance.models import Ordonnance
from .models import LigneOrdonnance
from .ligneServices import LigneOrdonnanceService
from .ligneRepositories import LigneOrdonnanceRepository


class LigneOrdonnanceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.service = LigneOrdonnanceService()
        self.repo = LigneOrdonnanceRepository()

        # Admin
        self.admin_user = User.objects.create(
            login="admin_test",
            email="admin@test.com",
            telephone="+224620000001",
            role=User.Role.ADMINISTRATEUR,
            actif=True
        )
        self.admin_user.set_password("AdminPass123!")
        self.admin_user.save()

        # Medecin
        self.medecin_user = User.objects.create(
            nom="Tounkara",
            prenom="Moussa",
            login="dr_moussa",
            email="dr.moussa@test.com",
            telephone="+224620000002",
            role=User.Role.MEDECIN,
            actif=True
        )
        self.medecin_user.set_password("DocPass123!")
        self.medecin_user.save()
        self.medecin = Medecin.objects.create(
            id_utilisateur=self.medecin_user,
            specialite=Medecin.Specialite.GENERALISTE,
            numero_ordre="CNOM-11223",
            date_embauche="2025-01-01"
        )

        # Autre Medecin
        self.other_medecin_user = User.objects.create(
            nom="Camara",
            prenom="Fanta",
            login="dr_fanta",
            email="dr.fanta@test.com",
            telephone="+224620000003",
            role=User.Role.MEDECIN,
            actif=True
        )
        self.other_medecin_user.set_password("DocPass123!")
        self.other_medecin_user.save()
        self.other_medecin = Medecin.objects.create(
            id_utilisateur=self.other_medecin_user,
            specialite=Medecin.Specialite.CARDIOLOGIE,
            numero_ordre="CNOM-99887",
            date_embauche="2025-01-01"
        )

        # Patient
        self.patient_user = User.objects.create(
            nom="Diallo",
            prenom="Ibrahima",
            login="patient_ibrahima",
            email="ibrahima@test.com",
            telephone="+224620000004",
            role=User.Role.PATIENT,
            actif=True
        )
        self.patient_user.set_password("PatientPass123!")
        self.patient_user.save()

        self.patient = Patient.objects.create(
            id_utilisateur=self.patient_user,
            sexe=Patient.Sexe.MASCULIN,
            groupe_sanguin=Patient.GroupeSanguin.O_POSITIF,
            adresse="Conakry",
            personne_a_contacter="Mère",
            date_inscription="2025-01-01"
        )

        # Consultation
        self.consultation = Consultation.objects.create(
            patient=self.patient,
            medecin=self.medecin,
            diagnostic="Paludisme simple",
            actif=True
        )

        # Ordonnance
        self.ordonnance = Ordonnance.objects.create(
            consultation=self.consultation,
            reference="ORD-TEST-001",
            observation="Traitement antipaludique standard",
            actif=True
        )

    def test_create_ligne_ordonnance_model_and_history(self):
        """Vérifie la création du modèle et la traçabilité de l'audit simple_history."""
        ligne = LigneOrdonnance.objects.create(
            ordonnance=self.ordonnance,
            medicament="Artéméther + Luméfantrine",
            dosage="20mg/120mg",
            forme="Comprimé",
            posologie="4 comprimés matin et soir",
            duree_traitement="3 jours",
            quantite=1,
            instructions="Prendre avec un repas gras"
        )
        self.assertEqual(ligne.idLigne, ligne.id)
        self.assertEqual(ligne.medicament, "Artéméther + Luméfantrine")
        self.assertIn("Artéméther", str(ligne))

        # Vérification de l'audit history
        history_records = ligne.history.all()
        self.assertGreaterEqual(history_records.count(), 1)
        self.assertEqual(history_records.first().medicament, "Artéméther + Luméfantrine")

    def test_service_create_and_query_lignes(self):
        """Test des méthodes du service LigneOrdonnanceService."""
        ligne = self.service.create_ligne(
            ordonnance=self.ordonnance,
            medicament="Paracétamol",
            dosage="1000 mg",
            forme="Comprimé",
            posologie="1 comprimé toutes les 8 heures si fièvre",
            quantite=2
        )
        self.assertIsNotNone(ligne.pk)

        lignes = self.service.get_by_ordonnance(self.ordonnance.pk)
        self.assertEqual(lignes.count(), 1)
        self.assertEqual(lignes.first().medicament, "Paracétamol")

        search_res = self.service.search_lignes("para")
        self.assertEqual(search_res.count(), 1)

    def test_api_doctor_can_create_ligne_for_own_consultation(self):
        """Un médecin peut ajouter une ligne pour sa propre consultation."""
        self.client.force_authenticate(user=self.medecin_user)
        payload = {
            "idOrdonnance": self.ordonnance.id,
            "medicament": "Amoxicilline",
            "dosage": "1g",
            "forme": "Comprimé",
            "posologie": "1 comprimé 3 fois par jour",
            "dureeTraitement": "7 jours",
            "quantite": 2,
            "instructions": "Au cours du repas"
        }
        res = self.client.post("/lignes_ordonnances/", payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["medicament"], "Amoxicilline")
        self.assertEqual(res.data["dosage"], "1g")

    def test_api_doctor_cannot_modify_other_doctor_prescription(self):
        """Un autre médecin ne peut pas altérer l'ordonnance d'un confrère."""
        ligne = LigneOrdonnance.objects.create(
            ordonnance=self.ordonnance,
            medicament="Ibuprofène",
            dosage="400 mg",
            posologie="1 cp si douleur"
        )
        self.client.force_authenticate(user=self.other_medecin_user)
        res = self.client.patch(f"/lignes_ordonnances/{ligne.id}/", {"dosage": "600 mg"}, format="json")
        self.assertEqual(res.status_code, 403)

    def test_api_patient_can_view_own_prescription_lines(self):
        """Un patient peut consulter les lignes de sa propre ordonnance."""
        ligne = LigneOrdonnance.objects.create(
            ordonnance=self.ordonnance,
            medicament="Vitamine C",
            dosage="500 mg",
            posologie="1 cp le matin"
        )
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.get(f"/lignes_ordonnances/{ligne.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["medicament"], "Vitamine C")

    def test_api_admin_can_hard_delete_ligne(self):
        """L'administrateur peut supprimer définitivement une ligne."""
        ligne = LigneOrdonnance.objects.create(
            ordonnance=self.ordonnance,
            medicament="Aspirine",
            dosage="100 mg",
            posologie="1 cp par jour"
        )
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(f"/lignes_ordonnances/{ligne.id}/?hard=true")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(LigneOrdonnance.objects.filter(pk=ligne.id).exists())
