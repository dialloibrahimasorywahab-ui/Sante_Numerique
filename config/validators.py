import re
from datetime import date, datetime
from django.core.exceptions import ValidationError


def validate_phone_number(value: str):
    """
    Valide un numéro de téléphone (format international E.164 ou local standard, 8 à 15 chiffres).
    Exemples acceptés : '+224622001122', '+33612345678', '0102030405', '0700000000'.
    """
    if not value:
        return value
    clean_val = re.sub(r'[\s\.\-\(\)]', '', str(value).strip())
    pattern = r'^\+?[0-9]{8,15}$'
    if not re.match(pattern, clean_val):
        raise ValidationError(
            "Numéro de téléphone invalide. Doit comporter entre 8 et 15 chiffres (ex: +224622001122 ou 0102030405)."
        )
    return value


def validate_date_not_in_future(value):
    """
    Vérifie qu'une date (naissance, décès, inscription) ne se situe pas dans le futur.
    """
    if not value:
        return value
    if isinstance(value, datetime):
        val_date = value.date()
    elif isinstance(value, date):
        val_date = value
    elif isinstance(value, str):
        try:
            val_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return value
    else:
        return value

    if val_date > date.today():
        raise ValidationError("La date ne peut pas être située dans le futur.")
    return value


def validate_strict_positive(value):
    """
    Vérifie qu'un montant ou une quantité numérique est strictement supérieur(e) à zéro.
    """
    if value is not None:
        try:
            num = float(value)
            if num <= 0:
                raise ValidationError("La valeur doit être strictement supérieure à zéro.")
        except (ValueError, TypeError):
            raise ValidationError("Valeur numérique invalide.")
    return value


def validate_social_security_number(value: str):
    """
    Valide le numéro de sécurité sociale / identification nationale (NIR).
    Doit comporter entre 8 et 20 caractères alphanumériques.
    """
    if not value:
        return value
    clean_val = str(value).strip()
    if not re.match(r'^[0-9A-Z]{8,20}$', clean_val, re.IGNORECASE):
        raise ValidationError(
            "Numéro de sécurité sociale / NIR invalide (8 à 20 caractères alphanumériques requis)."
        )
    return value


def validate_blood_group(value: str):
    """
    Valide le groupe sanguin parmi les 8 standards ABO et rhésus (+/-).
    """
    if not value:
        return value
    val = str(value).strip().upper()
    valid_groups = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    if val not in valid_groups:
        raise ValidationError(
            f"Groupe sanguin '{value}' non valide. Valeurs autorisées: {', '.join(sorted(valid_groups))}."
        )
    return value


def validate_numero_ordre(value: str):
    """
    Valide le numéro d'ordre des médecins (ex: CNOM-12345).
    """
    if not value:
        return value
    clean_val = str(value).strip()
    if len(clean_val) < 3:
        raise ValidationError("Le numéro d'ordre doit comporter au moins 3 caractères.")
    return value


def validate_nouveau_ne_metrics(poids=None, taille=None):
    """
    Valide le poids (0.3 à 7.0 kg) et la taille (20.0 à 70.0 cm) d'un nouveau-né.
    """
    if poids is not None:
        try:
            p = float(poids)
            if p < 0.3 or p > 7.0:
                raise ValidationError("Le poids du nouveau-né doit être compris entre 0.3 kg et 7.0 kg.")
        except (ValueError, TypeError):
            raise ValidationError("Poids du nouveau-né invalide.")

    if taille is not None:
        try:
            t = float(taille)
            if t < 20.0 or t > 70.0:
                raise ValidationError("La taille du nouveau-né doit être comprise entre 20.0 cm et 70.0 cm.")
        except (ValueError, TypeError):
            raise ValidationError("Taille du nouveau-né invalide.")
