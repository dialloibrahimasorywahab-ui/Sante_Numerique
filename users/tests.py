from django.contrib.auth.hashers import check_password
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from users.usersRepositories import UserRepository
from users.usersServices import UserService


class UserServiceTests(TestCase):
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


