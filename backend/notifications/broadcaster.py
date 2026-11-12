import json
import logging
import queue
import threading
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class Subscriber:
    def __init__(self, q: queue.Queue, user_id: Optional[int] = None, role: Optional[str] = None):
        self.queue = q
        self.user_id = user_id
        self.role = role

    def is_authorized(self, event_data: dict) -> bool:
        dest_role = event_data.get("destinataireRole") or event_data.get("destinataire_role")
        dest_user_id = event_data.get("destinataireUserId") or event_data.get("destinataire_user_id")

        # 1. Si la notification est expressément ciblée sur un identifiant utilisateur précis
        if dest_user_id is not None:
            return self.user_id == dest_user_id

        # 2. Cloisonnement strict : les patients ne doivent JAMAIS recevoir les alertes internes hospitalières (lits, salle d'attente, etc.)
        if self.role == "PATIENT":
            return dest_role == "PATIENT"

        # 3. Le rôle TOUS correspond au personnel hospitalier soignant et administratif (Admins, Médecins, Infirmiers)
        if dest_role == "TOUS":
            return self.role in ["ADMINISTRATEUR", "MEDECIN", "INFIRMIER"]

        if dest_role == "ADMINISTRATEUR":
            return self.role == "ADMINISTRATEUR"

        if dest_role == "MEDECIN":
            return self.role in ["MEDECIN", "ADMINISTRATEUR"]

        if dest_role == "INFIRMIER":
            return self.role in ["INFIRMIER", "ADMINISTRATEUR"]

        return False


class NotificationBroadcaster:
    """
    Gestionnaire Pub/Sub en mémoire, thread-safe, pour la diffusion
    d'événements temps réel (Server-Sent Events) avec filtrage strict par rôle.
    """

    def __init__(self):
        self._subscribers: Dict[queue.Queue, Subscriber] = {}
        self._lock = threading.Lock()

    def subscribe(self, user_id: Optional[int] = None, role: Optional[str] = None) -> queue.Queue:
        """Enregistre un nouveau client SSE avec ses informations d'accréditation et de rôle."""
        q: queue.Queue = queue.Queue(maxsize=100)
        sub = Subscriber(q=q, user_id=user_id, role=role)
        with self._lock:
            self._subscribers[q] = sub
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        """Désinscrit un client SSE à la fermeture de la connexion HTTP."""
        with self._lock:
            self._subscribers.pop(q, None)

    def publish(self, event_data: dict) -> None:
        """Diffuse un événement formaté uniquement aux abonnés autorisés."""
        json_payload = json.dumps(event_data, ensure_ascii=False)
        sse_message = f"data: {json_payload}\n\n"

        with self._lock:
            subscribers_snapshot = list(self._subscribers.values())

        for sub in subscribers_snapshot:
            if not sub.is_authorized(event_data):
                continue

            try:
                sub.queue.put_nowait(sse_message)
            except queue.Full:
                try:
                    sub.queue.get_nowait()
                    sub.queue.put_nowait(sse_message)
                except Exception:
                    pass


# Instance singleton du broadcaster
broadcaster = NotificationBroadcaster()

