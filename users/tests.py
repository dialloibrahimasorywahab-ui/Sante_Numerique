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
        client = APIClient()
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

    def test_create_user_partial_data_returns_400(self):
        client = APIClient()
        response = client.post("/users/", {"nom": "Chirurgie Chorale"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("prenom", response.data)
        self.assertIn("email", response.data)
        self.assertIn("telephone", response.data)
        self.assertIn("login", response.data)

