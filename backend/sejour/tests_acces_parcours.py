"""
Tests de contrôle d'accès sur le parcours patient :
séjour (synthèse, statistiques), localisation, mouvement, événement.

Règles vérifiées :
- le personnel (médecin, infirmier, administrateur) accède à tout ;
- un patient ne voit que ses propres séjours et ne peut rien écrire ;
- un utilisateur non authentifié est refusé.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.test_helpers import creer_test_patient, creer_test_utilisateur
from evenement.models import EvenementParcours
from localisation.models import LocalisationPatient
from mouvement.models import MouvementPatient
from sejour.models import Sejour
from sejour.sejourServices import SejourService
from services.models import Service


def _items(response):
    """Extrait la liste d'éléments d'une réponse paginée ou non."""
    data = response.data
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


class AccesParcoursPatientTests(TestCase):
    def setUp(self):
        self.admin = creer_test_utilisateur("acces_admin", role="ADMINISTRATEUR")
        self.infirmier = creer_test_utilisateur("acces_infirmier", role="INFIRMIER")

        self.service_urgences = Service.objects.create(nom_service="Urgences", actif=True)

        self.patient_a = creer_test_patient("acces_patient_a")
        self.patient_b = creer_test_patient("acces_patient_b")

        svc = SejourService()
        self.sejour_a = svc.admettre_patient(
            data={
                "patient": self.patient_a.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "type_prise_en_charge": Sejour.TypePriseEnCharge.URGENCE,
                "motif_admission": "Séjour du patient A",
            },
            user=self.admin,
        )
        self.sejour_b = svc.admettre_patient(
            data={
                "patient": self.patient_b.id_patient,
                "service_responsable": self.service_urgences.id_service,
                "type_prise_en_charge": Sejour.TypePriseEnCharge.URGENCE,
                "motif_admission": "Séjour du patient B",
            },
            user=self.admin,
        )

        self.loc_a = LocalisationPatient.objects.get(sejour=self.sejour_a, est_actuelle=True)
        self.mvt_a = MouvementPatient.objects.filter(sejour=self.sejour_a).first()
        self.evt_a = EvenementParcours.objects.filter(sejour=self.sejour_a).first()

        self.client = APIClient()

    # ------------------------------------------------------------------ anonyme
    def test_anonyme_refuse_partout(self):
        urls = [
            reverse("sejour-synthese", args=[self.sejour_a.id_sejour]),
            reverse("sejour-dashboard-stats"),
            reverse("localisation-list-create"),
            reverse("evenement-list-create"),
            reverse("mouvement-list"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ synthèse
    def test_patient_ne_peut_pas_lire_la_synthese_d_un_autre_patient(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        url = reverse("sejour-synthese", args=[self.sejour_a.id_sejour])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_peut_lire_sa_propre_synthese(self):
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        url = reverse("sejour-synthese", args=[self.sejour_a.id_sejour])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_personnel_peut_lire_toute_synthese(self):
        self.client.force_authenticate(user=self.infirmier)
        for sejour in (self.sejour_a, self.sejour_b):
            url = reverse("sejour-synthese", args=[sejour.id_sejour])
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------ statistiques
    def test_statistiques_dashboard_reservees_au_personnel(self):
        url = reverse("sejour-dashboard-stats")
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.infirmier)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------ localisation
    def test_patient_ne_voit_que_ses_localisations_dans_la_liste(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(reverse("localisation-list-create"), {"est_actuelle": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in _items(response)}
        self.assertNotIn(self.loc_a.id, ids)
        self.assertEqual(len(ids), 1)  # uniquement sa propre localisation

    def test_personnel_voit_toutes_les_localisations(self):
        self.client.force_authenticate(user=self.infirmier)
        response = self.client.get(reverse("localisation-list-create"), {"est_actuelle": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(_items(response)), 2)

    def test_patient_ne_peut_pas_lire_le_detail_d_une_localisation_d_autrui(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        url = reverse("localisation-detail", args=[self.loc_a.id])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_ne_peut_pas_deplacer_un_patient(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.post(
            reverse("localisation-list-create"),
            {"sejour": self.sejour_a.id_sejour, "service": self.service_urgences.id_service},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # La localisation du patient A n'a pas bougé
        self.assertEqual(
            LocalisationPatient.objects.filter(sejour=self.sejour_a, est_actuelle=True).count(), 1
        )

    # ------------------------------------------------------------------ événements
    def test_patient_ne_peut_pas_creer_d_evenement_clinique(self):
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        avant = EvenementParcours.objects.filter(sejour=self.sejour_a).count()
        response = self.client.post(
            reverse("evenement-list-create"),
            {"sejour": self.sejour_a.id_sejour, "titre": "Injection", "type_evenement": "OBSERVATION"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(EvenementParcours.objects.filter(sejour=self.sejour_a).count(), avant)

    def test_patient_ne_voit_pas_les_evenements_d_autrui(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(reverse("evenement-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in _items(response)}
        self.assertNotIn(self.evt_a.id, ids)

    def test_patient_ne_peut_pas_lire_le_detail_d_un_evenement_d_autrui(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        url = reverse("evenement-detail", args=[self.evt_a.id])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------ mouvements
    def test_patient_ne_voit_pas_les_mouvements_d_autrui(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(reverse("mouvement-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in _items(response)}
        self.assertNotIn(self.mvt_a.id, ids)

    def test_patient_ne_peut_pas_lire_le_detail_d_un_mouvement_d_autrui(self):
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        url = reverse("mouvement-detail", args=[self.mvt_a.id])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
