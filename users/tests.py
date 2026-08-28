from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from users.usersRepositories import UserRepository
from users.usersServices import UserService


class UserServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_create_user_hashes_password(self):
        service = UserService()
        user = service.createUser(
            nom="Doe",
            prenom="John",
            email="john@example.com",
            telephone="0102030405",
            login="johndoe",
            motDePasseHash="monMotDePasse123",
            role=User.Role.MEDECIN,
        )
        self.assertNotEqual(user.motDePasseHash, "monMotDePasse123")
        self.assertTrue(check_password("monMotDePasse123", user.motDePasseHash))

    def test_get_non_existent_user_returns_none(self):
        repository = UserRepository()
        user = repository.getUser(9999)
        self.assertIsNone(user)

    def test_get_user_api_not_found_returns_404(self):
        admin = User.objects.create(nom="Admin", prenom="Super", email="adm@test.com", telephone="0101010101", login="adm_usr", motDePasseHash="hash", role=User.Role.ADMINISTRATEUR)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.get("/users/9999/")
        self.assertEqual(response.status_code, 404)

    def test_login_user_success(self):
        service = UserService()
        user = service.createUser(
            nom="Martin",
            prenom="Paul",
            email="paul@example.com",
            telephone="0700000000",
            login="pmartin",
            motDePasseHash="secr3tPassword",
            role=User.Role.MEDECIN,
        )

        client = APIClient()
        response = client.post("/users/login/", {"login": "pmartin", "motDePasse": "secr3tPassword"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["idUser"], user.idUser)

    def test_login_user_invalid_credentials(self):
        client = APIClient()
        response = client.post("/users/login/", {"login": "inconnu", "motDePasse": "wrong"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_login_user_with_email_success(self):
        service = UserService()
        user = service.createUser(
            nom="Konan",
            prenom="Yves",
            email="yves.konan@example.com",
            telephone="0711223344",
            login="ykonan",
            motDePasseHash="myPassWord123",
            role=User.Role.MEDECIN,
        )

        client = APIClient()
        response = client.post("/users/login/", {"login": "yves.konan@example.com", "motDePasse": "myPassWord123"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["idUser"], user.idUser)

    def test_login_user_sets_jwt_cookies(self):
        service = UserService()
        user = service.createUser(
            nom="Dupont",
            prenom="Claire",
            email="claire.dupont@example.com",
            telephone="0799887766",
            login="cdupont",
            motDePasseHash="monPasswordSecurise123",
            role=User.Role.MEDECIN,
        )

        client = APIClient()
        response = client.post("/users/login/", {"login": "cdupont", "motDePasse": "monPasswordSecurise123"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_logout_user_clears_cookies(self):
        client = APIClient()
        client.cookies["access_token"] = "fake_access"
        client.cookies["refresh_token"] = "fake_refresh"
        response = client.post("/users/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Déconnexion réussie.")

    def test_token_refresh_via_cookie(self):
        service = UserService()
        user = service.createUser(
            nom="Sissoko",
            prenom="Moussa",
            email="moussa@example.com",
            telephone="0788776655",
            login="msissoko",
            motDePasseHash="pass12345",
            role=User.Role.ADMINISTRATEUR,
        )

        client = APIClient()
        login_res = client.post("/users/login/", {"login": "msissoko", "motDePasse": "pass12345"}, format="json")
        refresh_cookie = login_res.cookies["refresh_token"].value

        # Client refresh request with cookie
        refresh_client = APIClient()
        refresh_client.cookies["refresh_token"] = refresh_cookie
        refresh_res = refresh_client.post("/users/token/refresh/")
        self.assertEqual(refresh_res.status_code, 200)
        self.assertIn("access_token", refresh_res.cookies)

    def test_infirmier_and_patient_cannot_create_users(self):
        user_inf = User.objects.create(nom="Inf", prenom="Test", email="inf_u@test.com", telephone="0101010199", login="inf_u", motDePasseHash="hash", role=User.Role.INFIRMIER)
        user_pat = User.objects.create(nom="Pat", prenom="Test", email="pat_u@test.com", telephone="0101010198", login="pat_u", motDePasseHash="hash", role=User.Role.PATIENT)

        client = APIClient()
        payload = {
            "nom": "Diallo",
            "prenom": "Oumar",
            "email": "oumar.diallo@example.com",
            "telephone": "0700112233",
            "login": "oumar_d",
            "motDePasse": "Pass12345!",
            "role": "PATIENT"
        }

        # 1. INFIRMIER -> 403 Forbidden
        client.force_authenticate(user=user_inf)
        res_inf = client.post("/users/", payload, format="json")
        self.assertEqual(res_inf.status_code, 403)

        # 2. PATIENT -> 403 Forbidden
        client.force_authenticate(user=user_pat)
        res_pat = client.post("/users/", payload, format="json")
        self.assertEqual(res_pat.status_code, 403)

    def test_unauthenticated_cannot_escalate_role_to_admin(self):
        """Vérifie qu'un utilisateur anonyme ne peut jamais créer de compte ADMINISTRATEUR ou MEDECIN (forcé PATIENT)."""
        client = APIClient()
        payload = {
            "nom": "Hacker",
            "prenom": "Attacker",
            "email": "hacker@example.com",
            "telephone": "0700998877",
            "login": "fake_admin",
            "motDePasse": "HackedPass123!",
            "role": "ADMINISTRATEUR"  # Tentative d'injection de rôle
        }

        # POST /users/ anonyme
        res = client.post("/users/", payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["role"], "PATIENT")

        # Vérification en base de données : le compte créé est bien PATIENT
        created_user = User.objects.get(login="fake_admin")
        self.assertEqual(created_user.role, User.Role.PATIENT)

        # Connexion avec ce compte
        login_res = client.post("/users/login/", {"login": "fake_admin", "motDePasse": "HackedPass123!"}, format="json")
        self.assertEqual(login_res.status_code, 200)

        # Tentative d'accéder aux endpoints d'administration -> 403 Forbidden
        get_all_res = client.get("/users/all/")
        self.assertEqual(get_all_res.status_code, 403)

    def test_unauthenticated_get_users_is_protected(self):
        """GET /users/ sans authentification renvoie 401 Unauthorized."""
        client = APIClient()
        res = client.get("/users/")
        self.assertEqual(res.status_code, 401)

    def test_login_rate_limiting_applies(self):
        """Vérifie que le throttle bloque après dépassement de la limite de tentatives de connexion."""
        from django.core.cache import cache
        cache.clear()
        client = APIClient()

        # Envoi de 5 tentatives rapides de login
        for _ in range(5):
            client.post("/users/login/", {"login": "wrong_user", "motDePasse": "wrong_pass"}, format="json")

        # La 6ème tentative doit être bloquée par le throttling (HTTP 429 Too Many Requests)
        res = client.post("/users/login/", {"login": "wrong_user", "motDePasse": "wrong_pass"}, format="json")
        self.assertEqual(res.status_code, 429)
        cache.clear()





