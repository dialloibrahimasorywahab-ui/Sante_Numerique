from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


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


class IsOwnerOrStaff(BasePermission):
    """
    Permission pour les patients (accès restreint à leurs propres données)
    et le personnel soignant / administrateurs (accès étendu).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, "role", None)
        if role in ["ADMINISTRATEUR", "MEDECIN", "INFIRMIER"]:
            return True

        if role == "PATIENT":
            # Si l'objet est directement l'utilisateur
            if obj == request.user:
                return True
            # Si l'objet a un lien idUtilisateur (ex: Patient, Personnel, Medecin)
            if getattr(obj, "idUtilisateur", None) == request.user:
                return True
            # Si l'objet a un lien patient (ex: RendezVous, Consultation, Hospitalisation)
            patient = getattr(obj, "patient", None)
            if patient:
                if patient == request.user or getattr(patient, "idUtilisateur", None) == request.user:
                    return True
            # Si l'objet a un lien consultation (ex: Ordonnance, LigneOrdonnance, FraisConsultation)
            consultation = getattr(obj, "consultation", None)
            if consultation:
                c_patient = getattr(consultation, "patient", None)
                if c_patient and (c_patient == request.user or getattr(c_patient, "idUtilisateur", None) == request.user):
                    return True
            # Si l'objet a un lien hospitalisation
            hospitalisation = getattr(obj, "hospitalisation", None)
            if hospitalisation:
                h_patient = getattr(hospitalisation, "patient", None)
                if h_patient and (h_patient == request.user or getattr(h_patient, "idUtilisateur", None) == request.user):
                    return True
            # Si l'objet a un lien user
            if getattr(obj, "user", None) == request.user:
                return True

        return False


def deny_unless_owner_or_staff(request, obj):
    """
    Helper pour les vues fonctionnelles (@api_view) :
    Vérifie que l'utilisateur connecté est soit le propriétaire de l'objet (patient),
    soit un membre du personnel autorisé (Médecin, Infirmier, Administrateur).
    Lève une PermissionDenied (403) si le contrôle échoue.
    """
    if not request.user or not request.user.is_authenticated:
        raise PermissionDenied("Authentification requise.")

    role = getattr(request.user, "role", None)
    if role in ["ADMINISTRATEUR", "MEDECIN", "INFIRMIER"]:
        return True

    if role == "PATIENT":
        # Vérification d'appartenance
        if obj == request.user:
            return True
        if getattr(obj, "idUtilisateur", None) == request.user:
            return True
        patient = getattr(obj, "patient", None)
        if patient:
            if patient == request.user or getattr(patient, "idUtilisateur", None) == request.user:
                return True
        consultation = getattr(obj, "consultation", None)
        if consultation:
            c_patient = getattr(consultation, "patient", None)
            if c_patient and (c_patient == request.user or getattr(c_patient, "idUtilisateur", None) == request.user):
                return True
        hospitalisation = getattr(obj, "hospitalisation", None)
        if hospitalisation:
            h_patient = getattr(hospitalisation, "patient", None)
            if h_patient and (h_patient == request.user or getattr(h_patient, "idUtilisateur", None) == request.user):
                return True
        if getattr(obj, "user", None) == request.user:
            return True

    raise PermissionDenied("Vous n'êtes pas autorisé à accéder ou modifier cette ressource.")
