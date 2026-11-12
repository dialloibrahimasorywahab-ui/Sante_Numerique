from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_user_admin(user) -> bool:
    """Vérifie si un utilisateur dispose des droits administrateur."""
    if not user or not user.is_authenticated:
        return False
    return bool(
        getattr(user, 'is_superuser', False)
        or getattr(user, 'is_staff', False)
        or getattr(user, 'role', None) == 'ADMINISTRATEUR'
    )


class IsAdminOrReadOnly(BasePermission):
    """
    Lecture publique ouverte à tous.
    Écriture (création, modification, suppression) strictement réservée aux administrateurs.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_user_admin(request.user)


class IsAdminUserOnly(BasePermission):
    """
    Accès strictement réservé aux administrateurs (lecture et écriture).
    """
    def has_permission(self, request, view):
        return is_user_admin(request.user)

