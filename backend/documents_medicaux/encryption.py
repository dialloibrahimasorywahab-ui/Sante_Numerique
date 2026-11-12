import base64
import hashlib
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_cipher() -> Fernet:
    """
    Génère une clé de chiffrement Fernet (AES-128-CBC + HMAC-SHA256)
    dérivée de manière déterministe depuis le SECRET_KEY du projet Django.
    Garantit le chiffrement fort au repos des données de santé (HDS).
    """
    secret = getattr(settings, 'SECRET_KEY', 'default-sante-numerique-secret-key').encode('utf-8')
    salt = b'sante-numerique-ged-encryption-salt-v1'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret))
    return Fernet(key)


def encrypt_bytes(data: bytes) -> bytes:
    """Chiffre les octets du fichier médical avant stockage sur disque ou object storage."""
    cipher = _get_cipher()
    return cipher.encrypt(data)


def decrypt_bytes(encrypted_data: bytes) -> bytes:
    """Déchiffre les octets du fichier médical pour consultation sécurisée."""
    cipher = _get_cipher()
    return cipher.decrypt(encrypted_data)


def calculate_sha256(data: bytes) -> str:
    """Calcule l'empreinte cryptographique SHA-256 du fichier original pour garantir son intégrité."""
    return hashlib.sha256(data).hexdigest()
