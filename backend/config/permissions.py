from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Accès réservé exclusivement aux administrateurs."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMINISTRATEUR"
        )


class IsMedecinOuAdmin(BasePermission):
    """Accès réservé aux médecins et administrateurs."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in ["MEDECIN", "ADMINISTRATEUR"]
        )


class IsStaffOrAdmin(BasePermission):
    """Accès réservé au personnel médical (Médecins, Infirmiers) et administrateurs."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]
        )


class IsStaffOrAdminReadOnly_IsMedecinOuAdminWrite(BasePermission):
    """
    Lecture autorisée pour tout le personnel (Médecin, Infirmier, Admin).
    Écriture (création/modification/suppression) réservée aux Médecins et Administrateurs.
    """
    message = "Accès refusé. Seul un médecin ou un administrateur peut enregistrer ou modifier cette ressource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        if request.method in SAFE_METHODS:
            return role in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]
        return role in ["MEDECIN", "ADMINISTRATEUR"]


class IsStaffOrAdminReadOnly_IsAdminWrite(BasePermission):
    """
    Lecture autorisée pour le personnel et les admins.
    Écriture réservée exclusivement aux Administrateurs.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        if request.method in SAFE_METHODS:
            return role in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]
        return role == "ADMINISTRATEUR"


class IsAuthenticatedReadOnly_IsStaffOrAdminWrite(BasePermission):
    """
    Lecture pour tous les utilisateurs connectés.
    Écriture pour le personnel médical et administrateurs.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, "role", None) in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]


def _check_object_ownership(user, obj) -> bool:
    """
    Vérifie si l'utilisateur donné est le propriétaire direct ou indirect de l'objet.
    """
    if obj is None or user is None:
        return False
    if obj == user:
        return True
    if getattr(obj, "id_user", None) is not None and getattr(obj, "id_user", None) == getattr(user, "id_user", None):
        return True

    # Lien direct via idUtilisateur / id_utilisateur / user
    direct_user = getattr(obj, "idUtilisateur", None) or getattr(obj, "id_utilisateur", None) or getattr(obj, "user", None)
    if direct_user is not None:
        if direct_user == user or getattr(direct_user, "pk", None) == getattr(user, "pk", None):
            return True

    # Lien via patient
    patient = getattr(obj, "patient", None) or getattr(obj, "id_patient", None)
    if patient is not None:
        if patient == user or getattr(patient, "pk", None) == getattr(user, "pk", None):
            return True
        p_user = getattr(patient, "idUtilisateur", None) or getattr(patient, "id_utilisateur", None)
        if p_user is not None and (p_user == user or getattr(p_user, "pk", None) == getattr(user, "pk", None)):
            return True

    # Lien via consultation
    consultation = getattr(obj, "consultation", None)
    if consultation is not None:
        c_patient = getattr(consultation, "patient", None)
        if c_patient is not None:
            if c_patient == user or getattr(c_patient, "pk", None) == getattr(user, "pk", None):
                return True
            cp_user = getattr(c_patient, "idUtilisateur", None) or getattr(c_patient, "id_utilisateur", None)
            if cp_user is not None and (cp_user == user or getattr(cp_user, "pk", None) == getattr(user, "pk", None)):
                return True

    # Lien via hospitalisation
    hospitalisation = getattr(obj, "hospitalisation", None)
    if hospitalisation is not None:
        h_patient = getattr(hospitalisation, "patient", None)
        if h_patient is not None:
            if h_patient == user or getattr(h_patient, "pk", None) == getattr(user, "pk", None):
                return True
            hp_user = getattr(h_patient, "idUtilisateur", None) or getattr(h_patient, "id_utilisateur", None)
            if hp_user is not None and (hp_user == user or getattr(hp_user, "pk", None) == getattr(user, "pk", None)):
                return True

    return False


def _is_account_or_profile_object(obj) -> bool:
    """
    Identifie si l'objet est un compte utilisateur ou un profil de praticien/personnel
    (User, Medecin, Personnel), pour lesquels les règles d'étanchéité de compte s'appliquent.
    """
    if obj is None:
        return False
    # Vérification User
    if hasattr(obj, "role") and hasattr(obj, "email") and hasattr(obj, "login"):
        return True
    # Vérification Medecin ou Personnel
    if hasattr(obj, "numero_ordre") or hasattr(obj, "specialite") or hasattr(obj, "matricule"):
        return True
    return False


class IsOwnerOrStaff(BasePermission):
    """
    Permission pour les patients (accès restreint à leurs propres données)
    et le personnel soignant / administrateurs (accès étendu aux dossiers médicaux).
    Pour les comptes utilisateurs et profils personnels, seuls le propriétaire ou l'administrateur
    ont l'autorisation d'accès et de modification (protection contre l'usurpation).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, "role", None)

        # L'administrateur a tous les droits
        if role == "ADMINISTRATEUR":
            return True

        # Le propriétaire légitime a toujours accès
        if _check_object_ownership(request.user, obj):
            return True

        # Pour les comptes et profils personnels, aucun médecin ou infirmier tiers ne peut y accéder
        if _is_account_or_profile_object(obj):
            return False

        # Pour les dossiers médicaux hospitaliers, le personnel soignant a accès
        if role in ["MEDECIN", "INFIRMIER"]:
            return True

        return False


def deny_unless_owner_or_staff(request, obj=None, *args, **kwargs):
    """
    Helper pour les vues fonctionnelles (@api_view) :
    Vérifie que l'utilisateur connecté est soit le propriétaire de l'objet,
    soit un administrateur, soit un soignant pour les données médicales autorisées.

    CORRECTION PROBLÈME 2 :
    - Un utilisateur peut modifier uniquement son propre profil dans les limites des champs autorisés.
    - Seul un administrateur peut modifier le compte d'un autre utilisateur.
    - Un médecin ou infirmier ne peut JAMAIS modifier ou désactiver le compte ou profil d'un autre praticien ou utilisateur.
    Lève une PermissionDenied (403) si le contrôle échoue.
    """
    if not request.user or not request.user.is_authenticated:
        raise PermissionDenied("Authentification requise.")

    role = getattr(request.user, "role", None)

    # Administrateur a tous les droits administratifs
    if role == "ADMINISTRATEUR":
        return True

    # Vérification de propriété directe / indirecte
    if _check_object_ownership(request.user, obj):
        return True

    # Pour un compte utilisateur ou profil professionnel (User, Medecin, Personnel),
    # un non-propriétaire et non-administrateur ne peut JAMAIS accéder ou modifier
    if _is_account_or_profile_object(obj):
        raise PermissionDenied("Vous n'êtes pas autorisé à accéder ou modifier ce compte ou profil.")

    # Pour les dossiers de soins / médicaux (consultations, ordonnances, séjours),
    # les soignants ont accès dans le cadre de leurs fonctions
    if role in ["MEDECIN", "INFIRMIER"]:
        return True

    raise PermissionDenied("Vous n'êtes pas autorisé à accéder ou modifier cette ressource.")


# ---------------------------------------------------------------------------
# Contrôle d'accès au parcours patient (séjour, localisation, mouvement, événement)
# ---------------------------------------------------------------------------
STAFF_ROLES = ("ADMINISTRATEUR", "MEDECIN", "INFIRMIER")


def is_staff_role(user) -> bool:
    """True si l'utilisateur connecté est du personnel soignant ou administrateur."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) in STAFF_ROLES
    )


def scope_to_accessible_sejours(request, queryset, sejour_lookup: str = "sejour"):
    """
    Restreint un queryset aux séjours que l'utilisateur a le droit de voir :
    - personnel / administrateur : tout ;
    - patient : uniquement les objets rattachés à ses propres séjours ;
    - tout autre rôle : rien.
    """
    user = request.user
    if is_staff_role(user):
        return queryset
    if getattr(user, "role", None) == "PATIENT":
        return queryset.filter(**{f"{sejour_lookup}__patient__id_utilisateur": user})
    return queryset.none()


def ensure_can_access_sejour(request, sejour) -> bool:
    """
    Contrôle d'accès à un séjour précis (vues de détail / synthèse).
    Lève PermissionDenied (403) si l'utilisateur n'est ni du personnel
    ni le patient concerné par ce séjour.
    """
    user = request.user
    if is_staff_role(user):
        return True
    if (
        getattr(user, "role", None) == "PATIENT"
        and sejour is not None
        and sejour.patient.id_utilisateur_id == user.pk
    ):
        return True
    raise PermissionDenied("Vous n'êtes pas autorisé à accéder à ce séjour.")
