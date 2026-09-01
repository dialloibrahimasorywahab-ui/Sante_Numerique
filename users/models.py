# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, login, email=None, password=None, **extra_fields):
        if not login:
            raise ValueError("Le login est obligatoire")
        email = self.normalize_email(email) if email else ""
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("actif", True)

        nom = extra_fields.get("nom", "")
        prenom = extra_fields.get("prenom", "")
        if nom and not extra_fields.get("last_name"):
            extra_fields["last_name"] = nom
        if prenom and not extra_fields.get("first_name"):
            extra_fields["first_name"] = prenom

        user = self.model(username=login, login=login, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, login, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMINISTRATEUR")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(login, email, password, **extra_fields)


class User(AbstractUser):

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"
        MEDECIN = "MEDECIN", "Medecin"
        INFIRMIER = "INFIRMIER", "Infirmier"

    id_user = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150, blank=False)
    prenom = models.CharField(max_length=150, blank=False)
    email = models.EmailField(max_length=150, unique=True, blank=False)
    telephone = models.CharField(max_length=20, unique=True, blank=False)
    login = models.CharField(max_length=150, unique=True, blank=False)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )

    date_naissance = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["email", "nom", "prenom"]

    def save(self, *args, **kwargs):
        self.username = self.login
        self.first_name = self.prenom
        self.last_name = self.nom
        self.is_active = self.actif
        super().save(*args, **kwargs)

    # Propriétés snake_case standard
    @property
    def mot_de_passe_hash(self):
        return self.password

    @mot_de_passe_hash.setter
    def mot_de_passe_hash(self, raw_password):
        if raw_password:
            if raw_password.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                self.password = raw_password
            else:
                self.set_password(raw_password)

    @property
    def derniere_connexion(self):
        return self.last_login

    @derniere_connexion.setter
    def derniere_connexion(self, val):
        self.last_login = val

    # Propriétés de compatibilité camelCase
    @property
    def idUser(self):
        return self.id_user

    @idUser.setter
    def idUser(self, val):
        self.id_user = val

    @property
    def dateNaissance(self):
        return self.date_naissance

    @dateNaissance.setter
    def dateNaissance(self, val):
        self.date_naissance = val

    @property
    def motDePasseHash(self):
        return self.mot_de_passe_hash

    @motDePasseHash.setter
    def motDePasseHash(self, val):
        self.mot_de_passe_hash = val

    @property
    def derniereConnexion(self):
        return self.derniere_connexion

    @derniereConnexion.setter
    def derniereConnexion(self, val):
        self.derniere_connexion = val

    def __str__(self):
        return f"{self.login} ({self.prenom} {self.nom})"