from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import deny_unless_owner_or_staff
from config.schema_helpers import HARD_DELETE_PARAM, PAGINATION_PARAMS, SEARCH_PARAM, ErrorResponseSerializer, MessageResponseSerializer
from .models import DocumentMedical
from .serializers import DocumentMedicalSerializer, DocumentUploadSerializer
from .services import DocumentMedicalService

document_service = DocumentMedicalService()


@extend_schema(
    tags=["Documents Médicaux (GED)"],
    summary="Lister ou téléverser un document médical",
    description="Retourne la liste des documents médicaux chiffrés (GET) ou téléverse un nouveau document/imagerie (POST multipart).",
    parameters=[
        OpenApiParameter(name="patient", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                         description="Filtrer par identifiant du patient"),
        OpenApiParameter(name="categorie", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                         description="Filtrer par catégorie (RADIO, SCANNER, IRM, ANALYSE_SANG, ORDONNANCE, CERTIFICAT, etc.)"),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=DocumentUploadSerializer,
    responses={
        200: DocumentMedicalSerializer(many=True),
        201: DocumentMedicalSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def list_create_documents(request):
    user = request.user
    role = getattr(user, 'role', None)

    if request.method == "GET":
        patient_id = request.query_params.get("patient")
        categorie = request.query_params.get("categorie")
        search_q = request.query_params.get("search") or request.query_params.get("q")

        # Cloisonnement strict pour les patients : ne voir QUE leurs propres documents
        if role == "PATIENT":
            patient_profile = getattr(user, 'patient', None)
            if not patient_profile:
                return Response([], status=status.HTTP_200_OK)
            patient_id = patient_profile.id_patient

        if search_q:
            qs = document_service.repository.search_documents(
                query=search_q,
                patient_id=int(patient_id) if patient_id else None,
                categorie=categorie,
                actif_only=True
            )
        elif patient_id:
            qs = document_service.repository.get_by_patient(
                patient_id=int(patient_id),
                categorie=categorie,
                actif_only=True
            )
        else:
            qs = document_service.repository.get_all(actif_only=True, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur', 'consultation'])
            if categorie:
                qs = qs.filter(categorie__iexact=categorie)

        return paginate_response(qs, request, DocumentMedicalSerializer)

    # POST : Téléversement d'un document
    serializer = DocumentUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    patient = serializer.validated_data["patient"]

    # Si c'est un patient connecté, il ne peut téléverser que dans son propre dossier
    if role == "PATIENT":
        patient_profile = getattr(user, 'patient', None)
        if not patient_profile or patient_profile.id_patient != patient.id_patient:
            return Response(
                {"error": "Vous n'êtes pas autorisé à téléverser un document pour un autre patient."},
                status=status.HTTP_403_FORBIDDEN
            )

    # Si c'est un médecin connecté, associer automatiquement son profil médecin
    medecin = serializer.validated_data.get("medecin")
    if role == "MEDECIN" and not medecin:
        medecin = getattr(user, 'medecin', None)

    document = document_service.upload_document(
        patient=patient,
        titre=serializer.validated_data["titre"],
        uploaded_file=serializer.validated_data["fichier"],
        categorie=serializer.validated_data.get("categorie", DocumentMedical.Categorie.AUTRE),
        medecin=medecin,
        consultation=serializer.validated_data.get("consultation"),
        date_document=serializer.validated_data.get("date_document"),
        observation=serializer.validated_data.get("observation", "")
    )

    output_serializer = DocumentMedicalSerializer(document, context={"request": request})
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Documents Médicaux (GED)"],
    summary="Détail, modification ou suppression d'un document médical",
    parameters=[HARD_DELETE_PARAM],
    request=DocumentMedicalSerializer,
    responses={
        200: DocumentMedicalSerializer,
        400: ErrorResponseSerializer,
        403: MessageResponseSerializer,
        404: MessageResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def get_document_detail(request, document_id: int):
    document = document_service.get_by_id(document_id, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur'])
    if not document:
        return Response({"message": "Document médical introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, document)

    if request.method == "DELETE":
        hard = request.query_params.get("hard", "false").lower() == "true"
        # Seul un administrateur peut faire un hard delete
        if hard and getattr(request.user, 'role', None) != "ADMINISTRATEUR":
            return Response({"error": "Suppression définitive réservée aux administrateurs."}, status=status.HTTP_403_FORBIDDEN)
        document_service.delete(document, hard=hard)
        return Response({"message": "Document médical archivé avec succès."}, status=status.HTTP_200_OK)

    if request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        for field in ["titre", "categorie", "observation", "date_document"]:
            if field in request.data:
                setattr(document, field, request.data[field])
        document.save()
        serializer = DocumentMedicalSerializer(document, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = DocumentMedicalSerializer(document, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Documents Médicaux (GED)"],
    summary="Télécharger ou visualiser un document médical déchiffré",
    description="Déchiffre le document médical à la volée et le renvoie en streaming avec vérification d'intégrité SHA-256.",
    parameters=[
        OpenApiParameter(name="download", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False,
                         description="Si true, force le téléchargement du fichier en pièce jointe"),
    ],
    responses={
        200: OpenApiTypes.BINARY,
        403: MessageResponseSerializer,
        404: MessageResponseSerializer,
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_document_file(request, document_id: int):
    document = document_service.get_by_id(document_id, select_related=['patient__id_utilisateur', 'medecin__id_utilisateur'])
    if not document or not document.fichier:
        return Response({"message": "Fichier médical introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, document)

    try:
        decrypted_bytes, filename, mime_type = document_service.get_decrypted_content(document)
    except Exception as e:
        return Response({"error": f"Erreur lors du déchiffrement sécurisé du document: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    force_download = request.query_params.get("download", "false").lower() == "true"
    disposition = "attachment" if force_download else "inline"

    response = HttpResponse(decrypted_bytes, content_type=mime_type or "application/octet-stream")
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    response["Content-Length"] = len(decrypted_bytes)
    response["X-Checksum-SHA256"] = document.checksum_sha256
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    return response
