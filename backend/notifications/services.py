from typing import Optional, List
from django.db.models import QuerySet, Q
from common.repositories import BaseRepository
from common.services import BaseService
from .models import NotificationHospitaliere
from .broadcaster import broadcaster


class NotificationService(BaseService[NotificationHospitaliere]):
    """
    Service gérant la création, l'archivage et la diffusion temps réel
    des alertes et notifications hospitalières.
    """

    def __init__(self):
        super().__init__(repository=BaseRepository(model=NotificationHospitaliere))

    def emettre_notification(
        self,
        type_notification: str,
        titre: str,
        message: str,
        destinataire_role: str = NotificationHospitaliere.DestinataireRole.TOUS,
        destinataire_user=None,
        donnees: Optional[dict] = None
    ) -> NotificationHospitaliere:
        """
        Persiste la notification en base et la diffuse instantanément
        via le flux SSE aux praticiens et administrateurs connectés.
        """
        donnees = donnees or {}
        notif = self.create(
            type_notification=type_notification,
            titre=titre,
            message=message,
            destinataire_role=destinataire_role,
            destinataire_user=destinataire_user,
            donnees=donnees
        )

        # Diffusion temps réel SSE
        event_payload = {
            "id": notif.id_notification,
            "idNotification": notif.id_notification,
            "type": notif.type_notification,
            "typeNotification": notif.type_notification,
            "titre": notif.titre,
            "message": notif.message,
            "destinataireRole": notif.destinataire_role,
            "destinataireUserId": notif.destinataire_user_id,
            "donnees": notif.donnees,
            "dateCreation": notif.date_creation.isoformat(),
        }
        broadcaster.publish(event_payload)

        return notif

    def get_notifications_pour_utilisateur(
        self,
        user,
        non_lues_seulement: bool = False
    ) -> QuerySet[NotificationHospitaliere]:
        """Retourne les notifications visibles pour un utilisateur donné selon son rôle."""
        role = getattr(user, 'role', None)
        qs = self.get_all(actif_only=True)

        if role == "ADMINISTRATEUR":
            qs = qs.filter(Q(destinataire_role__in=["ADMINISTRATEUR", "TOUS"]) | Q(destinataire_user=user))
        elif role == "MEDECIN":
            qs = qs.filter(Q(destinataire_role__in=["MEDECIN", "TOUS"]) | Q(destinataire_user=user))
        elif role == "INFIRMIER":
            qs = qs.filter(Q(destinataire_role__in=["INFIRMIER", "TOUS"]) | Q(destinataire_user=user))
        elif role == "PATIENT":
            qs = qs.filter(destinataire_user=user)
        else:
            qs = qs.filter(destinataire_user=user)

        if non_lues_seulement:
            qs = qs.filter(lu=False)

        return qs

    def marquer_comme_lue(self, notif_id: int, user) -> bool:
        """Marque une notification comme lue."""
        qs = self.get_notifications_pour_utilisateur(user)
        notif = qs.filter(pk=notif_id).first()
        if notif:
            notif.lu = True
            notif.save(update_fields=['lu'])
            return True
        return False

    def marquer_tout_comme_lu(self, user) -> int:
        """Marque toutes les notifications non lues de l'utilisateur comme lues."""
        qs = self.get_notifications_pour_utilisateur(user, non_lues_seulement=True)
        return qs.update(lu=True)
