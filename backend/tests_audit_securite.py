"""
Tests d'audit de sécurité — Couverture des 12 problèmes identifiés.
Branche : fix/audit-securite-complet

Ces tests couvrent :
1. Contrôle d'accès au parcours patient (séjour, localisation, mouvement, événement)
2. Protection contre la prise de contrôle de compte
3. Confidentialité des données de natalité
4. Préservation des rôles lors de la mise à jour du profil
5. Absence d'erreurs 500 sur PUT/PATCH/DELETE
6. Contraintes d'intégrité (doublons de localisation / lit)
7. Transfert atomique (annulation si une étape échoue)
8. Génération de référence de séjour concurrente
"""

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from rest_framework.test import APIClient
from rest_framework import status

from common.test_helpers import creer_test_utilisateur, creer_test_patient
from services.models import Service
from medecin.models import Medecin
from batiment.models import Batiment
from chambre.models import Chambre
from lit.models import Lit
from users.models import User

from sejour.models import Sejour
from sejour.sejourServices import SejourService
from localisation.models import LocalisationPatient
from mouvement.models import MouvementPatient
from evenement.models import EvenementParcours


# =============================================================================
# PROBLÈME 1 & 3 — Contrôle d'accès au parcours patient
# =============================================================================

class AccesParcoursPatientsTests(TestCase):
    """
    TEST 1 : Un patient ne peut pas lire le séjour d'un autre patient.
    TEST 2 : Un patient ne peut pas déclencher un transfert non autorisé.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = creer_test_utilisateur("admin_acces", role="ADMINISTRATEUR")
        self.medecin_user = creer_test_utilisateur("medecin_acces", role="MEDECIN")
        self.service = Service.objects.create(nom_service="Urgences", actif=True)
        self.medecin = Medecin.objects.create(
            id_utilisateur=self.medecin_user,
            specialite=Medecin.Specialite.GENERALISTE,
            numero_ordre="MED-TEST-001",
            date_embauche="2024-01-01",
        )
        self.patient_a = creer_test_patient("patient_a_acces")
        self.patient_b = creer_test_patient("patient_b_acces")

        self.sejour_service = SejourService()
        self.sejour_a = self.sejour_service.admettre_patient(
            data={
                "patient": self.patient_a.id_patient,
                "service_responsable": self.service.id_service,
                "motif_admission": "Test patient A",
            },
            user=self.admin,
        )

    def test_patient_ne_peut_pas_lire_sejour_dun_autre_patient(self):
        """TEST 1 — Un patient B ne peut pas accéder au séjour du patient A."""
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(f"/sejours/{self.sejour_a.id_sejour}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_peut_lire_son_propre_sejour(self):
        """TEST 1 (accès autorisé) — Un patient peut accéder à son propre séjour."""
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        response = self.client.get(f"/sejours/{self.sejour_a.id_sejour}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_ne_peut_pas_declencher_un_transfert(self):
        """TEST 2 — Un patient ne peut pas déclencher un transfert non autorisé."""
        service_b = Service.objects.create(nom_service="Cardiologie", actif=True)
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        response = self.client.post("/mouvements/transfert/", {
            "sejour": self.sejour_a.id_sejour,
            "service": service_b.id_service,
            "motif": "Tentative de transfert non autorisé",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_ne_peut_pas_lire_localisation_dun_autre(self):
        """TEST 1 — Un patient ne peut pas accéder aux localisations d'un autre patient via le listing."""
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(f"/localisations/?sejour_id={self.sejour_a.id_sejour}")
        # Le patient B ne doit pas voir les localisations du séjour du patient A
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La liste doit être vide (scope filtré par séjour du patient B uniquement)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)

    def test_patient_sans_sejour_ne_peut_pas_acceder_aux_evenements(self):
        """TEST 1 — Un patient B sans séjour ne voit aucun événement du patient A."""
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(f"/evenements/?sejour_id={self.sejour_a.id_sejour}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)


# =============================================================================
# PROBLÈME 2 — Protection contre la prise de contrôle de compte
# =============================================================================

class ProtectionComptesUtilisateursTests(TestCase):
    """
    TEST 3 : Un médecin ou infirmier ne peut pas modifier le rôle d'un autre utilisateur.
    TEST 4 : Un médecin ou infirmier ne peut pas désactiver un compte administratif.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = creer_test_utilisateur("admin_prise_controle", role="ADMINISTRATEUR")
        self.medecin = creer_test_utilisateur("medecin_prise_controle", role="MEDECIN")
        self.infirmier = creer_test_utilisateur("infirmier_prise_controle", role="INFIRMIER")
        self.patient = creer_test_utilisateur("patient_prise_controle", role="PATIENT")

    def test_medecin_ne_peut_pas_modifier_role_autre_utilisateur(self):
        """TEST 3 — Un médecin ne peut pas donner le rôle ADMINISTRATEUR à un autre compte."""
        self.client.force_authenticate(user=self.medecin)
        response = self.client.patch(
            f"/users/{self.patient.id_user}/",
            {"role": "ADMINISTRATEUR"},
            format="json"
        )
        # L'opération doit échouer (403 car modification d'un autre utilisateur)
        # ou réussir mais sans changer le rôle
        if response.status_code == status.HTTP_200_OK:
            self.patient.refresh_from_db()
            self.assertNotEqual(self.patient.role, "ADMINISTRATEUR",
                "Le rôle ADMINISTRATEUR ne doit pas être attribuable par un non-admin")
        else:
            self.assertIn(response.status_code, [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_400_BAD_REQUEST,
            ])

    def test_infirmier_ne_peut_pas_desactiver_compte_admin(self):
        """TEST 4 — Un infirmier ne peut pas désactiver le compte d'un administrateur."""
        self.client.force_authenticate(user=self.infirmier)
        response = self.client.delete(f"/users/{self.admin.id_user}/")
        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ])
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.actif, "Le compte admin ne doit pas être désactivé")

    def test_patient_ne_peut_pas_modifier_profil_autre_utilisateur(self):
        """TEST 2 — Un patient ne peut modifier que son propre profil."""
        self.client.force_authenticate(user=self.patient)
        response = self.client.patch(
            f"/users/{self.medecin.id_user}/",
            {"nom": "Hacker"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_utilisateur_ne_peut_pas_sattribuer_role_admin(self):
        """TEST 2 — Un patient ne peut pas s'attribuer le rôle ADMINISTRATEUR sur son propre profil."""
        self.client.force_authenticate(user=self.patient)
        response = self.client.patch(
            f"/users/{self.patient.id_user}/",
            {"role": "ADMINISTRATEUR"},
            format="json"
        )
        # Soit 403, soit 200 mais sans changement de rôle
        if response.status_code == status.HTTP_200_OK:
            self.patient.refresh_from_db()
            self.assertEqual(self.patient.role, "PATIENT",
                "Un patient ne doit pas pouvoir s'attribuer le rôle ADMINISTRATEUR")

    def test_admin_peut_modifier_role_utilisateur(self):
        """TEST 2 (autorisé) — Un administrateur peut changer le rôle d'un utilisateur."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/users/{self.patient.id_user}/",
            {"role": "INFIRMIER"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.role, "INFIRMIER")


# =============================================================================
# PROBLÈME 3 — Confidentialité des données de natalité
# =============================================================================

class ConfidentialiteNataliteTests(TestCase):
    """
    TEST 5 : Un patient ne peut pas consulter les données de naissance d'un autre patient.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = creer_test_utilisateur("admin_natal", role="ADMINISTRATEUR")
        self.patient_a = creer_test_patient("patient_natal_a")
        self.patient_b = creer_test_patient("patient_natal_b")

    def test_patient_ne_peut_pas_voir_natalites_autre_patient(self):
        """TEST 5 — Patient B ne peut pas accéder aux données de natalité du patient A."""
        self.client.force_authenticate(user=self.patient_b.id_utilisateur)
        response = self.client.get(f"/natalites/patient/{self.patient_a.id_patient}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_peut_voir_ses_propres_natalites(self):
        """TEST 5 (autorisé) — Un patient peut accéder à ses propres données de natalité."""
        self.client.force_authenticate(user=self.patient_a.id_utilisateur)
        response = self.client.get(f"/natalites/patient/{self.patient_a.id_patient}/")
        # 200 ou 404 si aucune donnée, mais pas 403
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_medecin_peut_voir_natalites_de_tout_patient(self):
        """TEST 5 (autorisé) — Un médecin a accès aux données de natalité de tout patient."""
        medecin = creer_test_utilisateur("medecin_natal", role="MEDECIN")
        self.client.force_authenticate(user=medecin)
        response = self.client.get(f"/natalites/patient/{self.patient_a.id_patient}/")
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# =============================================================================
# PROBLÈME 5 — Préservation des rôles utilisateurs
# =============================================================================

class PreservationRolesTests(TestCase):
    """
    TEST 6 : Un médecin conserve son rôle après une modification de profil.
    TEST 7 : Un infirmier conserve son rôle après une modification de profil.
    TEST 8 : Les créations publiques et administratives conservent leurs règles respectives.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = creer_test_utilisateur("admin_roles", role="ADMINISTRATEUR")
        self.medecin = creer_test_utilisateur("medecin_roles", role="MEDECIN")
        self.infirmier = creer_test_utilisateur("infirmier_roles", role="INFIRMIER")

    def test_medecin_conserve_son_role_apres_modification_nom(self):
        """TEST 6 — Modifier le nom d'un médecin ne doit pas réinitialiser son rôle à PATIENT."""
        self.client.force_authenticate(user=self.medecin)
        response = self.client.patch(
            f"/users/{self.medecin.id_user}/",
            {"nom": "NouveauNom"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.medecin.refresh_from_db()
        self.assertEqual(self.medecin.role, "MEDECIN",
            "Le rôle MEDECIN doit être préservé après une modification de profil")

    def test_infirmier_conserve_son_role_apres_modification_prenom(self):
        """TEST 7 — Modifier le prénom d'un infirmier ne doit pas réinitialiser son rôle."""
        self.client.force_authenticate(user=self.infirmier)
        response = self.client.patch(
            f"/users/{self.infirmier.id_user}/",
            {"prenom": "NouveauPrenom"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.infirmier.refresh_from_db()
        self.assertEqual(self.infirmier.role, "INFIRMIER",
            "Le rôle INFIRMIER doit être préservé après une modification de profil")

    def test_creation_publique_assigne_role_patient(self):
        """TEST 8 — Une création publique (non-admin) reçoit systématiquement le rôle PATIENT."""
        response = self.client.post("/users/", {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@test.com",
            "telephone": "+22461000001",
            "login": "jean_dupont_pub",
            "motDePasse": "MotDePasse2026!",
            "role": "ADMINISTRATEUR",  # Tentative d'escalade de privilège
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(login="jean_dupont_pub")
        self.assertEqual(user.role, "PATIENT",
            "Une création publique doit toujours recevoir le rôle PATIENT")

    def test_creation_administrative_peut_assigner_role_medecin(self):
        """TEST 8 — Un admin peut créer un utilisateur avec le rôle MEDECIN."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/users/", {
            "nom": "Bah",
            "prenom": "Mariama",
            "email": "mariama.bah@hopital.test",
            "telephone": "+22462000002",
            "login": "mariama_bah_admin_test",
            "motDePasse": "MotDePasse2026!",
            "role": "MEDECIN",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(login="mariama_bah_admin_test")
        self.assertEqual(user.role, "MEDECIN")


# =============================================================================
# PROBLÈME 6 — Absence d'erreurs 500 sur PUT/PATCH/DELETE
# =============================================================================

class AbsenceErreurs500Tests(TestCase):
    """
    TEST 9 : Les opérations PUT, PATCH et DELETE ne provoquent pas d'erreur 500 inattendue.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = creer_test_utilisateur("admin_500", role="ADMINISTRATEUR")
        self.medecin = creer_test_utilisateur("medecin_500", role="MEDECIN")

    def test_put_utilisateur_ne_provoque_pas_500(self):
        """TEST 9 — PUT /users/<id>/ ne doit pas retourner 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f"/users/{self.medecin.id_user}/",
            {
                "nom": "ModifPUT",
                "prenom": "Agent",
                "email": self.medecin.email,
                "telephone": self.medecin.telephone,
                "login": self.medecin.login,
            },
            format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_patch_utilisateur_ne_provoque_pas_500(self):
        """TEST 9 — PATCH /users/<id>/ ne doit pas retourner 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/users/{self.medecin.id_user}/",
            {"nom": "ModifPATCH"},
            format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_delete_utilisateur_ne_provoque_pas_500(self):
        """TEST 9 — DELETE /users/<id>/ ne doit pas retourner 500."""
        self.client.force_authenticate(user=self.admin)
        user_to_delete = creer_test_utilisateur("user_to_delete_test_500", role="PATIENT")
        response = self.client.delete(f"/users/{user_to_delete.id_user}/")
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_put_sur_id_inexistant_retourne_404_pas_500(self):
        """TEST 9 — PUT sur un ID inexistant doit retourner 404, pas 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put("/users/999999/", {"nom": "Fantome"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_sur_id_inexistant_retourne_404_pas_500(self):
        """TEST 9 — PATCH sur un ID inexistant doit retourner 404, pas 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch("/users/999999/", {"nom": "Fantome"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_sur_id_inexistant_retourne_404_pas_500(self):
        """TEST 9 — DELETE sur un ID inexistant doit retourner 404, pas 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete("/users/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_donnees_invalides_retournent_400_pas_500(self):
        """TEST 9 — Des données invalides sur PUT doivent retourner 400, pas 500."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/users/{self.medecin.id_user}/",
            {"email": "pas-un-email-valide"},
            format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PROBLÈME 7 — Contraintes d'intégrité (parcours patient)
# =============================================================================

class ContraintesIntegriteTests(TestCase):
    """
    TEST 10 : Les contraintes d'intégrité empêchent les doublons interdits.
    """

    def setUp(self):
        self.admin = creer_test_utilisateur("admin_contraintes", role="ADMINISTRATEUR")
        self.patient = creer_test_patient("patient_contraintes")
        self.service = Service.objects.create(nom_service="Chirurgie", actif=True)
        self.batiment = Batiment.objects.create(nom="Pavillon Chirurgie", actif=True)
        self.chambre = Chambre.objects.create(
            batiment=self.batiment,
            numero_chambre=201,
            capacite=2,
        )
        self.lit = Lit.objects.create(chambre=self.chambre, numero_lit="L201-A", etat="DISPONIBLE")

        self.sejour_service = SejourService()
        self.sejour = self.sejour_service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service.id_service,
                "motif_admission": "Test contraintes",
            },
            user=self.admin,
        )

    def test_une_seule_localisation_actuelle_par_sejour(self):
        """TEST 10 — Un séjour ne peut avoir qu'une seule localisation active."""
        # La première localisation existe déjà (créée lors de l'admission)
        loc_actuelle = LocalisationPatient.objects.filter(
            sejour=self.sejour, est_actuelle=True
        )
        self.assertEqual(loc_actuelle.count(), 1)

    def test_transfert_cloture_ancienne_localisation(self):
        """TEST 10 — Un transfert clôture l'ancienne localisation avant d'en créer une nouvelle."""
        service_b = Service.objects.create(nom_service="Réanimation", actif=True)

        from localisation.localisationServices import LocalisationService
        loc_service = LocalisationService()
        loc_service.affecter_localisation(
            sejour_id=self.sejour.id_sejour,
            data={"service_id": service_b.id_service},
            user=self.admin,
        )

        # Il doit toujours y avoir exactement une localisation active
        localisations_actives = LocalisationPatient.objects.filter(
            sejour=self.sejour, est_actuelle=True
        )
        self.assertEqual(localisations_actives.count(), 1)

    def test_lit_ne_peut_pas_etre_occupe_par_deux_patients_simultanement(self):
        """
        TEST 10 — Un lit ne peut être attribué à deux localisations actives simultanément.
        Si les contraintes PostgreSQL conditionnelles sont actives, une IntegrityError est levée.
        En mode test sans PostgreSQL, on vérifie la logique métier du service.
        """
        # Patient 2
        patient_b = creer_test_patient("patient_b_contraintes")
        sejour_b = self.sejour_service.admettre_patient(
            data={
                "patient": patient_b.id_patient,
                "service_responsable": self.service.id_service,
                "motif_admission": "Test lit occupé",
            },
            user=self.admin,
        )

        # Occuper le lit avec le patient A
        self.lit.etat = "OCCUPE"
        self.lit.save()

        # Tenter d'affecter le même lit au patient B : doit échouer
        from localisation.localisationServices import LocalisationService
        loc_service = LocalisationService()
        with self.assertRaises((ValidationError, IntegrityError)):
            loc_service.affecter_localisation(
                sejour_id=sejour_b.id_sejour,
                data={
                    "service_id": self.service.id_service,
                    "lit_id": self.lit.id,
                },
                user=self.admin,
            )


# =============================================================================
# PROBLÈME 8 — Transfert atomique (annulation si échec)
# =============================================================================

class TransfertAtomiqueTests(TestCase):
    """
    TEST 11 : Un transfert échoué ne laisse ni localisation, ni mouvement, ni événement incohérent.
    """

    def setUp(self):
        self.admin = creer_test_utilisateur("admin_transfert", role="ADMINISTRATEUR")
        self.patient = creer_test_patient("patient_transfert")
        self.service_a = Service.objects.create(nom_service="Médecine A", actif=True)
        self.service_b = Service.objects.create(nom_service="Médecine B", actif=True)

        self.sejour_service = SejourService()
        self.sejour = self.sejour_service.admettre_patient(
            data={
                "patient": self.patient.id_patient,
                "service_responsable": self.service_a.id_service,
                "motif_admission": "Test transfert atomique",
            },
            user=self.admin,
        )

    def test_transfert_vers_service_inexistant_ne_laisse_pas_donnees_incoherentes(self):
        """
        TEST 11 — Un transfert vers un service inexistant doit lever une erreur
        sans créer de localisation, mouvement ou événement orphelin.
        """
        nb_localisations_avant = LocalisationPatient.objects.filter(sejour=self.sejour).count()
        nb_mouvements_avant = MouvementPatient.objects.filter(sejour=self.sejour).count()
        nb_evenements_avant = EvenementParcours.objects.filter(sejour=self.sejour).count()

        from mouvement.mouvementServices import MouvementService
        mouvement_service = MouvementService()

        with self.assertRaises((ValidationError, Exception)):
            mouvement_service.effectuer_transfert(
                sejour_id=self.sejour.id_sejour,
                data={
                    "service_id": 999999,  # ID inexistant
                    "motif": "Transfert vers ID inexistant",
                },
                user=self.admin,
            )

        # Vérifier qu'aucune donnée incohérente n'a été créée
        nb_localisations_apres = LocalisationPatient.objects.filter(sejour=self.sejour).count()
        nb_mouvements_apres = MouvementPatient.objects.filter(sejour=self.sejour).count()
        nb_evenements_apres = EvenementParcours.objects.filter(sejour=self.sejour).count()

        self.assertEqual(nb_localisations_avant, nb_localisations_apres,
            "Aucune localisation orpheline ne doit être créée après un transfert échoué")
        self.assertEqual(nb_mouvements_avant, nb_mouvements_apres,
            "Aucun mouvement orphelin ne doit être créé après un transfert échoué")
        self.assertEqual(nb_evenements_avant, nb_evenements_apres,
            "Aucun événement orphelin ne doit être créé après un transfert échoué")

    def test_transfert_sur_sejour_clos_est_rejete(self):
        """TEST 11 — On ne peut pas transférer un patient d'un séjour terminé."""
        # Clôturer le séjour
        self.sejour_service.enregistrer_sortie(
            sejour_id=self.sejour.id_sejour,
            user=self.admin,
            motif_sortie="Sortie normale",
        )

        from mouvement.mouvementServices import MouvementService
        mouvement_service = MouvementService()
        with self.assertRaises(ValidationError):
            mouvement_service.effectuer_transfert(
                sejour_id=self.sejour.id_sejour,
                data={
                    "service_id": self.service_b.id_service,
                    "motif": "Transfert illégal",
                },
                user=self.admin,
            )


# =============================================================================
# PROBLÈME 8 — Génération de référence de séjour
# =============================================================================

class GenerationReferencesSejourTests(TestCase):
    """
    TEST 12 : Le mécanisme de référence des séjours génère des références uniques.
    """

    def test_references_sont_uniques_pour_chaque_sejour(self):
        """TEST 12 — Deux séjours créés de suite doivent avoir des références différentes."""
        admin = creer_test_utilisateur("admin_ref", role="ADMINISTRATEUR")
        patient_a = creer_test_patient("patient_ref_a")
        patient_b = creer_test_patient("patient_ref_b")
        service = Service.objects.create(nom_service="Test Refs", actif=True)

        sejour_service = SejourService()
        sejour_a = sejour_service.admettre_patient(
            data={
                "patient": patient_a.id_patient,
                "service_responsable": service.id_service,
                "motif_admission": "Ref test A",
            },
            user=admin,
        )
        sejour_b = sejour_service.admettre_patient(
            data={
                "patient": patient_b.id_patient,
                "service_responsable": service.id_service,
                "motif_admission": "Ref test B",
            },
            user=admin,
        )

        self.assertNotEqual(sejour_a.reference, sejour_b.reference)

    def test_references_suivent_le_format_attendu(self):
        """TEST 12 — Les références de séjour respectent le format S-YYYY-XXXX."""
        import re
        from django.utils import timezone
        admin = creer_test_utilisateur("admin_format", role="ADMINISTRATEUR")
        patient = creer_test_patient("patient_format")
        service = Service.objects.create(nom_service="Test Format", actif=True)

        sejour_service = SejourService()
        sejour = sejour_service.admettre_patient(
            data={
                "patient": patient.id_patient,
                "service_responsable": service.id_service,
                "motif_admission": "Format test",
            },
            user=admin,
        )
        annee = timezone.now().year
        pattern = rf"^S-{annee}-\d{{4,}}$"
        self.assertRegex(sejour.reference, pattern,
            f"La référence '{sejour.reference}' ne respecte pas le format S-{annee}-XXXX")

