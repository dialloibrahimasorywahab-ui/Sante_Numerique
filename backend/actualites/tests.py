from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import CategorieActualite, Actualite

User = get_user_model()


class ActualiteTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Utilisateur normal (Patient)
        self.user_patient = User.objects.create_user(
            login="patient_test",
            email="patient@test.com",
            password="Password123!",
            nom="Diallo",
            prenom="Mamadou",
            telephone="+224600000001",
            role="PATIENT"
        )

        # Utilisateur Administrateur
        self.user_admin = User.objects.create_superuser(
            login="admin_test",
            email="admin@test.com",
            password="AdminPassword123!",
            nom="Bah",
            prenom="Fatoumata",
            telephone="+224600000002"
        )

        # Catégories de test
        self.cat_prevention, _ = CategorieActualite.objects.get_or_create(
            nom="Santé et prévention",
            defaults={
                "description": "Articles et conseils de santé publique",
                "couleur": "emerald",
                "actif": True
            }
        )
        self.cat_hopital, _ = CategorieActualite.objects.get_or_create(
            nom="Vie de l'hôpital",
            defaults={
                "description": "Nouvelles du centre hospitalier",
                "couleur": "blue",
                "actif": True
            }
        )

        # Articles
        self.art_publie = Actualite.objects.create(
            titre="Campagne de vaccination 2026",
            resume="Le centre hospitalier lance sa campagne annuelle.",
            contenu="Contenu détaillé sur la vaccination et les horaires d'ouverture.",
            categorie=self.cat_prevention,
            statut=Actualite.Statut.PUBLIE,
            est_a_la_une=True,
            date_publication=timezone.now()
        )

        self.art_brouillon = Actualite.objects.create(
            titre="Futur pavillon de cardiologie",
            resume="Projet d'agrandissement en cours de validation.",
            contenu="Note interne sur le calendrier des travaux.",
            categorie=self.cat_hopital,
            statut=Actualite.Statut.BROUILLON,
            est_a_la_une=False
        )

    def test_categorie_auto_slug(self):
        """Vérifie la génération automatique du slug pour les catégories."""
        cat, _ = CategorieActualite.objects.get_or_create(
            nom="Spécialités Pédiatriques",
            defaults={"description": "Soins des enfants"}
        )
        self.assertEqual(cat.slug, "specialites-pediatriques")

    def test_actualite_auto_slug_and_temps_lecture(self):
        """Vérifie le slug automatique et le calcul du temps de lecture."""
        self.assertTrue(self.art_publie.slug.startswith("campagne-de-vaccination-2026"))
        self.assertGreaterEqual(self.art_publie.temps_lecture, 1)

    def test_public_can_only_see_published_articles(self):
        """Le public ne doit voir que les articles au statut PUBLIE."""
        response = self.client.get("/api/actualites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # response.data can be list or paginated dict
        results = response.data.get("results", response.data)
        titres = [item.get("titre") for item in results]
        self.assertIn("Campagne de vaccination 2026", titres)
        self.assertNotIn("Futur pavillon de cardiologie", titres)

    def test_public_cannot_access_draft_detail(self):
        """Un visiteur essayant de charger un article brouillon reçoit 404."""
        response = self.client.get(f"/api/actualites/{self.art_brouillon.slug}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_access_draft_detail(self):
        """Un administrateur peut consulter le détail d'un article brouillon."""
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(f"/api/actualites/{self.art_brouillon.slug}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("titre"), "Futur pavillon de cardiologie")

    def test_admin_can_filter_by_statut(self):
        """Un administrateur peut filtrer par statut brouillon."""
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get("/api/actualites/?statut=BROUILLON")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("titre"), "Futur pavillon de cardiologie")

    def test_unauthorized_user_cannot_create_article(self):
        """Un utilisateur anonyme ou non-admin ne peut pas créer d'article."""
        payload = {
            "titre": "Article non autorisé",
            "resume": "Tentative de publication",
            "contenu": "Contenu interdit",
            "categorie": self.cat_prevention.id,
            "statut": "PUBLIE"
        }
        # Anonyme
        resp_anon = self.client.post("/api/actualites/", payload)
        self.assertIn(resp_anon.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Patient
        self.client.force_authenticate(user=self.user_patient)
        resp_patient = self.client.post("/api/actualites/", payload)
        self.assertEqual(resp_patient.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_and_update_article(self):
        """Un administrateur peut créer et modifier un article."""
        self.client.force_authenticate(user=self.user_admin)
        payload = {
            "titre": "Nouveau protocole d'hygiène",
            "resume": "Règles sanitaires actualisées pour les visiteurs.",
            "contenu": "Voici les détails complets du protocole sanitaire.",
            "categorie": self.cat_prevention.id,
            "statut": "PUBLIE",
            "est_a_la_une": False
        }
        resp = self.client.post("/api/actualites/", payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_id = resp.data.get("id")

        # Modification
        patch_payload = {"titre": "Nouveau protocole d'hygiène 2026"}
        resp_patch = self.client.patch(f"/api/actualites/{new_id}/", patch_payload)
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_patch.data.get("titre"), "Nouveau protocole d'hygiène 2026")

    def test_filter_by_search_and_category(self):
        """Vérifie le filtrage par recherche et par catégorie."""
        # Recherche par mot-clé
        resp_search = self.client.get("/api/actualites/?search=vaccination")
        results = resp_search.data.get("results", resp_search.data)
        self.assertEqual(len(results), 1)

        # Recherche par catégorie
        resp_cat = self.client.get(f"/api/actualites/?categorie={self.cat_prevention.id}")
        results_cat = resp_cat.data.get("results", resp_cat.data)
        self.assertEqual(len(results_cat), 1)

    def test_suggestions_endpoint(self):
        """Vérifie que l'endpoint de suggestions renvoie d'autres articles publiés."""
        # Créer un second article publié dans la même catégorie
        art2 = Actualite.objects.create(
            titre="Alimentation saine et coeur",
            resume="Conseils nutritionnels pour la santé cardiovasculaire.",
            contenu="Guide pratique sur les fruits, légumes et activité physique.",
            categorie=self.cat_prevention,
            statut=Actualite.Statut.PUBLIE,
            date_publication=timezone.now()
        )
        resp = self.client.get(f"/api/actualites/{self.art_publie.slug}/suggestions/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ne doit pas inclure l'article lui-même
        ids = [item.get("id") for item in resp.data]
        self.assertNotIn(self.art_publie.id, ids)
        self.assertIn(art2.id, ids)
