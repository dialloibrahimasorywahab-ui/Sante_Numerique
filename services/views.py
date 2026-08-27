from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsAdmin
from config.schema_helpers import ErrorResponseSerializer, HARD_DELETE_PARAM, MessageResponseSerializer, PAGINATION_PARAMS, SEARCH_PARAM
from .serviceSerializers import ServiceSerializer
from .serviceServices import ServiceService


service_service = ServiceService()


# Enregistrement et listing des services
@extend_schema(
    tags=["Services"],
    summary="Lister ou créer un service",
    description="Retourne la liste des services hospitaliers (GET avec ?search= optionnel) ou enregistre un nouveau service (POST).",
    parameters=[SEARCH_PARAM, *PAGINATION_PARAMS],
    request=ServiceSerializer,
    responses={200: ServiceSerializer(many=True), 201: ServiceSerializer, 400: ErrorResponseSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_service(request):
    if request.method == "GET":
        query = request.query_params.get("search") or request.query_params.get("q")
        if query:
            services = service_service.search_services(query)
        else:
            services = service_service.get_all_services()
        return paginate_response(services, request, ServiceSerializer)

    if getattr(request.user, "role", None) not in ["ADMINISTRATEUR"]:
        return Response({"error": "Seul un administrateur peut créer un service hospitalier."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ServiceSerializer(data=request.data)

    if serializer.is_valid():
        try:
            service = service_service.createService(**serializer.validated_data)
            serializer = ServiceSerializer(service)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un service avec ce nom existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Récupérer tous les services
@extend_schema(
    tags=["Services"],
    summary="Lister les services",
    description="Retourne la liste de tous les services hospitaliers.",
    parameters=[*PAGINATION_PARAMS],
    responses={200: ServiceSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_services(request):
    services = service_service.get_all_services()
    return paginate_response(services, request, ServiceSerializer)


# Récupérer, modifier ou supprimer un service grâce à son ID
@extend_schema(
    tags=["Services"],
    summary="Récupérer, modifier ou supprimer un service",
    description="Retourne, modifie ou supprime un service hospitalier à partir de son identifiant.",
    parameters=[HARD_DELETE_PARAM],
    request=ServiceSerializer,
    responses={200: ServiceSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_service(request, service_id):
    if request.method in ["PUT", "PATCH"]:
        return update_service(request, service_id)
    elif request.method == "DELETE":
        return delete_service(request, service_id)

    service = service_service.get_service(service_id)

    if service is None:
        return Response(
            {"message": "Service introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ServiceSerializer(service)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Modifier un service
@extend_schema(
    tags=["Services"],
    summary="Modifier un service",
    description="Met à jour totalement (PUT) ou partiellement (PATCH) un service.",
    request=ServiceSerializer,
    responses={200: ServiceSerializer, 400: ErrorResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAdmin])
def update_service(request, service_id):
    service = service_service.get_service(service_id)

    if service is None:
        return Response(
            {"message": "Service introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    partial = request.method == "PATCH" or request.data.get("partial", False)
    serializer = ServiceSerializer(service, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            service = service_service.update_service(service, **serializer.validated_data)
            serializer = ServiceSerializer(service)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except IntegrityError as e:
            return Response(
                {"error": "Un service avec ce nom existe déjà.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Désactiver (soft delete) ou supprimer un service
@extend_schema(
    tags=["Services"],
    summary="Supprimer / désactiver un service",
    description="Désactive (soft delete) le service, ou le supprime définitivement si ?hard=true.",
    parameters=[HARD_DELETE_PARAM],
    responses={200: MessageResponseSerializer, 404: MessageResponseSerializer},
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_service(request, service_id):
    service = service_service.get_service(service_id)

    if service is None:
        return Response(
            {"message": "Service introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    hard = str(request.query_params.get("hard", "")).lower() in ["true", "1"]
    service_service.delete_service(service, hard=hard)

    if hard:
        return Response(
            {"message": "Service supprimé définitivement avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(
        {"message": "Service désactivé (archivé) avec succès."},
        status=status.HTTP_200_OK
    )
