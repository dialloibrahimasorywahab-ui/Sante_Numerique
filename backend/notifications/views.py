import json
import queue
import time
from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsStaffOrAdmin
from config.schema_helpers import PAGINATION_PARAMS, ErrorResponseSerializer, MessageResponseSerializer
from .broadcaster import broadcaster
from .models import NotificationHospitaliere
from .serializers import NotificationHospitaliereSerializer, TriggerAlertSerializer
from .services import NotificationService

notification_service = NotificationService()


@extend_schema(
    tags=["Notifications & Temps Réel (SSE)"],
    summary="Flux d'événements et alertes temps réel (SSE)",
    description="Connexion HTTP persistante (Server-Sent Events) diffusant en direct les alertes hospitalières (lits d'urgence, arrivées patients, alertes cliniques).",
    responses={200: OpenApiTypes.STR},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stream_notifications(request):
    """
    Endpoint SSE (Server-Sent Events) pour les alertes instantanées.
    Envoie des pings heartbeat périodiques pour maintenir la connexion active.
    Filtre et diffuse uniquement les événements autorisés pour le rôle connecté.
    """
    user = request.user if request.user and request.user.is_authenticated else None
    user_id = getattr(user, 'id_user', None)
    role = getattr(user, 'role', None)

    def event_stream():
        client_queue = broadcaster.subscribe(user_id=user_id, role=role)
        # Message de bienvenue / confirmation de connexion SSE
        init_data = json.dumps({"type": "CONNECTED", "message": "Connexion temps réel Santé Numérique établie."})
        yield f"data: {init_data}\n\n"

        try:
            while True:
                try:
                    # Attente d'un événement pendant 15 secondes
                    msg = client_queue.get(timeout=15)
                    yield msg
                except queue.Empty:
                    # Heartbeat périodique pour éviter la déconnexion par les proxies / navigateurs
                    yield ": keep-alive\n\n"
        except GeneratorExit:
            broadcaster.unsubscribe(client_queue)
        except Exception:
            broadcaster.unsubscribe(client_queue)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"
    return response


@extend_schema(
    tags=["Notifications & Temps Réel (SSE)"],
    summary="Lister l'historique des notifications",
    parameters=[
        OpenApiParameter(name="unread", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                         description="Si true, filtre uniquement les notifications non lues"),
        *PAGINATION_PARAMS,
    ],
    responses={200: NotificationHospitaliereSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    unread_only = request.query_params.get("unread", "false").lower() == "true"
    qs = notification_service.get_notifications_pour_utilisateur(request.user, non_lues_seulement=unread_only)
    return paginate_response(qs, request, NotificationHospitaliereSerializer)


@extend_schema(
    tags=["Notifications & Temps Réel (SSE)"],
    summary="Marquer une notification comme lue",
    request=None,
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notif_id: int):
    success = notification_service.marquer_comme_lue(notif_id, request.user)
    if success:
        return Response({"message": "Notification marquée comme lue."}, status=status.HTTP_200_OK)
    return Response({"message": "Notification introuvable ou non autorisée."}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["Notifications & Temps Réel (SSE)"],
    summary="Marquer toutes les notifications comme lues",
    request=None,
    responses={200: MessageResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    count = notification_service.marquer_tout_comme_lu(request.user)
    return Response({"message": f"{count} notifications marquées comme lues."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Notifications & Temps Réel (SSE)"],
    summary="Déclencher manuellement une alerte hospitalière",
    description="Permet au personnel médical et aux administrateurs de diffuser une alerte prioritaire (ex: Lit d'urgence requis, Patient arrivé).",
    request=TriggerAlertSerializer,
    responses={201: NotificationHospitaliereSerializer, 400: ErrorResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsStaffOrAdmin])
def trigger_alert(request):
    serializer = TriggerAlertSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    notif = notification_service.emettre_notification(
        type_notification=serializer.validated_data["type_notification"],
        titre=serializer.validated_data["titre"],
        message=serializer.validated_data["message"],
        destinataire_role=serializer.validated_data.get("destinataire_role", NotificationHospitaliere.DestinataireRole.TOUS),
        donnees=serializer.validated_data.get("donnees", {})
    )

    out_serializer = NotificationHospitaliereSerializer(notif)
    return Response(out_serializer.data, status=status.HTTP_201_CREATED)
