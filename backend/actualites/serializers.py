from rest_framework import serializers
from .models import CategorieActualite, Actualite


class CategorieActualiteSerializer(serializers.ModelSerializer):
    total_articles = serializers.SerializerMethodField()

    class Meta:
        model = CategorieActualite
        fields = [
            'id',
            'nom',
            'slug',
            'description',
            'couleur',
            'icone',
            'actif',
            'date_creation',
            'total_articles',
        ]

    def get_total_articles(self, obj) -> int:
        return obj.actualites.filter(statut=Actualite.Statut.PUBLIE).count()


class ActualiteListSerializer(serializers.ModelSerializer):
    image = serializers.ReadOnlyField()
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    categorie_slug = serializers.CharField(source='categorie.slug', read_only=True)
    categorie_couleur = serializers.CharField(source='categorie.couleur', read_only=True)
    auteur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Actualite
        fields = [
            'id',
            'titre',
            'slug',
            'resume',
            'image',
            'image_couverture',
            'image_url',
            'categorie',
            'categorie_nom',
            'categorie_slug',
            'categorie_couleur',
            'auteur',
            'auteur_nom',
            'statut',
            'est_a_la_une',
            'temps_lecture',
            'vues',
            'date_publication',
            'date_creation',
        ]

    def get_auteur_nom(self, obj) -> str:
        if not obj.auteur:
            return "Équipe Médicale"
        prenom = getattr(obj.auteur, 'prenom', '')
        nom = getattr(obj.auteur, 'nom', '')
        full = f"{prenom} {nom}".strip()
        return full or obj.auteur.username


class ActualiteDetailSerializer(ActualiteListSerializer):
    class Meta(ActualiteListSerializer.Meta):
        fields = ActualiteListSerializer.Meta.fields + ['contenu', 'date_modification']


class ActualiteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actualite
        fields = [
            'id',
            'titre',
            'slug',
            'resume',
            'contenu',
            'categorie',
            'image_couverture',
            'image_url',
            'statut',
            'est_a_la_une',
            'date_publication',
        ]
        read_only_fields = ['id', 'slug']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('auteur', request.user)
        return super().create(validated_data)

