"""
Éléments réutilisés par les décorateurs @extend_schema (drf-spectacular)
dans les différentes apps du projet.

Ces sérialiseurs ne servent QUE à documenter la forme des réponses dans
Swagger/Redoc : ils ne sont jamais utilisés pour valider une requête réelle.
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers


class MessageResponseSerializer(serializers.Serializer):
    """Réponse générique contenant un simple message d'information (ex: 404, suppression réussie)."""
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    """Réponse générique d'erreur métier (ex: conflit d'unicité / IntegrityError)."""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)


class ValidationErrorResponseSerializer(serializers.Serializer):
    """Réponse générique d'erreur de validation (retour brut de serializer.errors)."""
    pass


# Paramètre de requête commun aux endpoints DELETE proposant une suppression définitive
HARD_DELETE_PARAM = OpenApiParameter(
    name="hard",
    type=OpenApiTypes.BOOL,
    location=OpenApiParameter.QUERY,
    required=False,
    description=(
        "Si 'true' ou '1' : suppression définitive de l'enregistrement. "
        "Sinon (par défaut) : désactivation (soft delete)."
    ),
)

SEARCH_PARAM = OpenApiParameter(
    name="search",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=False,
    description="Recherche textuelle libre (alias : q).",
)

PAGE_PARAM = OpenApiParameter(
    name="page",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    description="Numéro de la page à afficher (par défaut : 1).",
)

PAGE_SIZE_PARAM = OpenApiParameter(
    name="page_size",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    description="Nombre d'éléments par page (par défaut : 20, max : 100).",
)

PAGINATION_PARAMS = [PAGE_PARAM, PAGE_SIZE_PARAM]
