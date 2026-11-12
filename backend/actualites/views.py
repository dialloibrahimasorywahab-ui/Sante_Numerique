import logging
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.pagination import paginate_response
from .models import CategorieActualite, Actualite
from .permissions import IsAdminOrReadOnly, IsAdminUserOnly, is_user_admin
from .serializers import (
    CategorieActualiteSerializer,
    ActualiteListSerializer,
    ActualiteDetailSerializer,
    ActualiteWriteSerializer,
)

logger = logging.getLogger(__name__)


# ============================================================================
# GESTION DES CATÉGORIES
# ============================================================================

@extend_schema(
    tags=["Actualités"],
    summary="Lister les catégories d'actualités",
    responses={200: CategorieActualiteSerializer(many=True)},
)
@api_view(["GET", "POST"])
@permission_classes([IsAdminOrReadOnly])
def categories_list_create_view(request):
    """
    GET : Liste toutes les catégories actives (public).
    POST : Crée une nouvelle catégorie (administrateur uniquement).
    """
    if request.method == "GET":
        # Les admins peuvent voir toutes les catégories, le public seulement les actives
        if is_user_admin(request.user):
            categories = CategorieActualite.objects.all().order_by("nom")
        else:
            categories = CategorieActualite.objects.filter(actif=True).order_by("nom")
        serializer = CategorieActualiteSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = CategorieActualiteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Actualités"],
    summary="Détail, modification ou suppression d'une catégorie",
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
def categorie_detail_view(request, pk):
    """
    GET : Détail d'une catégorie.
    PUT / PATCH / DELETE : Modification ou suppression (Admin uniquement).
    """
    categorie = get_object_or_404(CategorieActualite, pk=pk)

    if request.method == "GET":
        serializer = CategorieActualiteSerializer(categorie)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not is_user_admin(request.user):
        return Response(
            {"detail": "Action réservée aux administrateurs."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        serializer = CategorieActualiteSerializer(categorie, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if categorie.actualites.exists():
            return Response(
                {"detail": "Impossible de supprimer une catégorie contenant des articles. Désactivez-la plutôt."},
                status=status.HTTP_400_BAD_REQUEST
            )
        categorie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# GESTION DES ACTUALITÉS
# ============================================================================

@extend_schema(
    tags=["Actualités"],
    summary="Lister ou créer des actualités",
    parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Recherche dans le titre, résumé et contenu"),
        OpenApiParameter(name="categorie", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filtre par ID ou Slug de la catégorie"),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filtre par statut (Admin uniquement : BROUILLON, PUBLIE)"),
        OpenApiParameter(name="est_a_la_une", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description="Filtre pour les articles à la une"),
        OpenApiParameter(name="ordering", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Tri (-date_publication, date_publication, -vues)"),
    ],
    responses={
        200: ActualiteListSerializer(many=True),
        201: ActualiteDetailSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAdminOrReadOnly])
def actualites_list_create_view(request):
    """
    GET : Liste paginée des actualités.
          - Visiteurs : uniquement les articles PUBLIÉS.
          - Administrateurs : tous les articles avec filtre possible sur le statut.
    POST : Création d'une actualité (Admin uniquement).
    """
    if request.method == "GET":
        qs = Actualite.objects.select_related("categorie", "auteur").all()

        user_is_admin = is_user_admin(request.user)
        statut_param = request.query_params.get("statut")

        if not user_is_admin:
            # Règle stricte de confidentialité : le public et les non-admins ne voient QUE les publiés
            qs = qs.filter(statut=Actualite.Statut.PUBLIE)
        elif statut_param:
            qs = qs.filter(statut=statut_param.upper())

        # Filtre catégorie (id ou slug)
        categorie_param = request.query_params.get("categorie")
        if categorie_param:
            if categorie_param.isdigit():
                qs = qs.filter(categorie_id=int(categorie_param))
            else:
                qs = qs.filter(Q(categorie__slug=categorie_param) | Q(categorie__nom__iexact=categorie_param))

        # Filtre à la une
        une_param = request.query_params.get("est_a_la_une")
        if une_param is not None:
            if une_param.lower() in ["true", "1"]:
                qs = qs.filter(est_a_la_une=True)
            elif une_param.lower() in ["false", "0"]:
                qs = qs.filter(est_a_la_une=False)

        # Recherche textuelle
        search_param = request.query_params.get("search")
        if search_param:
            search_param = search_param.strip()
            qs = qs.filter(
                Q(titre__icontains=search_param)
                | Q(resume__icontains=search_param)
                | Q(contenu__icontains=search_param)
            )

        # Tri
        ordering = request.query_params.get("ordering")
        allowed_orderings = [
            "date_publication", "-date_publication",
            "date_creation", "-date_creation",
            "vues", "-vues",
            "titre", "-titre"
        ]
        if ordering in allowed_orderings:
            qs = qs.order_by("-est_a_la_une", ordering)
        else:
            qs = qs.order_by("-est_a_la_une", "-date_publication", "-date_creation")

        return paginate_response(request, qs, ActualiteListSerializer)

    elif request.method == "POST":
        serializer = ActualiteWriteSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            article = serializer.save()
            read_serializer = ActualiteDetailSerializer(article, context={"request": request})
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Actualités"],
    summary="Consulter, modifier ou supprimer un article par slug ou ID",
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
def actualite_detail_view(request, slug_or_id):
    """
    GET : Détail complet d'un article.
          - Si l'article est un BROUILLON et que l'utilisateur n'est pas Admin : 404 Not Found.
          - Incrémente automatiquement le compteur de vues.
    PUT / PATCH / DELETE : Modification ou suppression (Admin uniquement).
    """
    # Recherche par ID ou slug
    qs = Actualite.objects.select_related("categorie", "auteur")
    if str(slug_or_id).isdigit():
        article = get_object_or_404(qs, id=int(slug_or_id))
    else:
        article = get_object_or_404(qs, slug=slug_or_id)

    # Protection des brouillons
    if article.statut == Actualite.Statut.BROUILLON and not is_user_admin(request.user):
        return Response(
            {"detail": "Article introuvable ou en cours de rédaction."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        # Incrémentation discrète des vues
        Actualite.objects.filter(pk=article.pk).update(vues=F("vues") + 1)
        article.refresh_from_db(fields=["vues"])
        serializer = ActualiteDetailSerializer(article, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Actions d'écriture réservées aux administrateurs
    if not is_user_admin(request.user):
        return Response(
            {"detail": "Action réservée aux administrateurs."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        serializer = ActualiteWriteSerializer(
            article,
            data=request.data,
            partial=partial,
            context={"request": request}
        )
        if serializer.is_valid():
            updated_article = serializer.save()
            read_serializer = ActualiteDetailSerializer(updated_article, context={"request": request})
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        article.delete()
        return Response(
            {"detail": "Article supprimé avec succès."},
            status=status.HTTP_204_NO_CONTENT
        )


@extend_schema(
    tags=["Actualités"],
    summary="Suggestions d'articles similaires ou récents",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def actualite_suggestions_view(request, slug_or_id):
    """
    Retourne jusqu'à 3 suggestions d'articles publiés :
    Priorité aux articles de la même catégorie, sinon les plus récents.
    """
    if str(slug_or_id).isdigit():
        current_article = get_object_or_404(Actualite, id=int(slug_or_id))
    else:
        current_article = get_object_or_404(Actualite, slug=slug_or_id)

    # Même catégorie d'abord
    same_cat = (
        Actualite.objects.filter(
            categorie=current_article.categorie,
            statut=Actualite.Statut.PUBLIE
        )
        .exclude(pk=current_article.pk)
        .order_by("-date_publication")[:3]
    )

    suggestions = list(same_cat)

    # Si moins de 3 articles, compléter avec les plus récents toutes catégories confondues
    if len(suggestions) < 3:
        needed = 3 - len(suggestions)
        existing_ids = [current_article.pk] + [a.pk for a in suggestions]
        other_recent = (
            Actualite.objects.filter(statut=Actualite.Statut.PUBLIE)
            .exclude(pk__in=existing_ids)
            .order_by("-date_publication")[:needed]
        )
        suggestions.extend(list(other_recent))

    serializer = ActualiteListSerializer(suggestions, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)

