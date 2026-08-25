from datetime import datetime
from typing import Optional

from django.db import models
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

    idUser = models.AutoField(primary_key=True)
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

    dateNaissance = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["email", "nom", "prenom"]

    def save(self, *args, **kwargs):
        self.username = self.login
        self.first_name = self.prenom
        self.last_name = self.nom
        self.is_active = self.actif
        if "update_fields" in kwargs and kwargs["update_fields"]:
            uf = set(kwargs["update_fields"])
            if "derniereConnexion" in uf:
                uf.remove("derniereConnexion")
                uf.add("last_login")
            if "actif" in uf:
                uf.add("is_active")
            if "nom" in uf:
                uf.add("last_name")
            if "prenom" in uf:
                uf.add("first_name")
            if "login" in uf:
                uf.add("username")
            kwargs["update_fields"] = list(uf)
        super().save(*args, **kwargs)

    @property
    def motDePasseHash(self):
        return self.password

    @motDePasseHash.setter
    def motDePasseHash(self, raw_password):
        if raw_password:
            if raw_password.startswith(("pbkdf2_", "bcrypt", "argon2", "scrypt")):
                self.password = raw_password
            else:
                self.set_password(raw_password)

    @property
    def derniereConnexion(self) -> Optional[datetime]:
        return self.last_login

    @derniereConnexion.setter
    def derniereConnexion(self, val):
        self.last_login = val

    def __str__(self):
        return f"{self.login} ({self.prenom} {self.nom})"