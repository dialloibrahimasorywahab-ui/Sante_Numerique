from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serviceSerializers import ServiceSerializer
from .serviceServices import ServiceService


service_service = ServiceService()


# Enregistrement d'un service
@api_view(["POST"])
def create_service(request):
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
@api_view(["GET"])
def get_all_services(request):
    services = service_service.get_all_services()
    serializer = ServiceSerializer(services, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# Récupérer et afficher un service par son ID
@api_view(["GET"])
def get_service(request, service_id):
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
@api_view(["PUT", "PATCH"])
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


# Supprimer un service
@api_view(["DELETE"])
def delete_service(request, service_id):
    service = service_service.get_service(service_id)

    if service is None:
        return Response(
            {"message": "Service introuvable"},
            status=status.HTTP_404_NOT_FOUND
        )

    service_service.delete_service(service)

    return Response(
        {"message": "Service supprimé avec succès"},
        status=status.HTTP_204_NO_CONTENT
    )
