from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class CategorieActualite(models.Model):
    """
    Catégories thématiques des actualités et conseils santé.
    Exemples: Vie de l'hôpital, Santé et prévention, Conseils médicaux, etc.
    """
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default='', verbose_name="Description")
    couleur = models.CharField(max_length=50, blank=True, default='emerald', verbose_name="Couleur du badge")
    icone = models.CharField(max_length=50, blank=True, default='newspaper', verbose_name="Icône")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie d'actualité"
        verbose_name_plural = "Catégories d'actualités"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom) or "categorie"
            slug = base_slug
            counter = 1
            while CategorieActualite.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Actualite(models.Model):
    """
    Articles d'actualités, publications médicales et conseils de prévention.
    """
    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', 'Brouillon'
        PUBLIE = 'PUBLIE', 'Publié'

    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255, verbose_name="Titre de l'article")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug URL")
    resume = models.TextField(verbose_name="Résumé de l'article", help_text="Bref aperçu accrocheur affiché sur les cartes")
    contenu = models.TextField(verbose_name="Contenu complet", help_text="Corps complet de l'article")
    
    # Image de couverture (upload de fichier local ou lien URL externe)
    image_couverture = models.FileField(
        upload_to='actualites/',
        null=True,
        blank=True,
        verbose_name="Fichier image de couverture"
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="URL externe de l'image (optionnelle)"
    )

    categorie = models.ForeignKey(
        CategorieActualite,
        on_delete=models.PROTECT,
        related_name='actualites',
        verbose_name="Catégorie"
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actualites',
        verbose_name="Auteur / Rédacteur"
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
        db_index=True,
        verbose_name="Statut de publication"
    )
    est_a_la_une = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Mettre à la une"
    )

    temps_lecture = models.PositiveIntegerField(
        default=3,
        verbose_name="Temps de lecture estimé (minutes)"
    )
    vues = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de vues"
    )

    date_publication = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Date de publication"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-est_a_la_une', '-date_publication', '-date_creation']

    def __str__(self):
        return f"{self.titre} ({self.get_statut_display()})"

    @property
    def image(self) -> str:
        """Retourne l'URL de l'image (upload local prioritaire, sinon image_url, sinon placeholder médical élégant)"""
        if self.image_couverture:
            try:
                return self.image_couverture.url
            except Exception:
                pass
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80'

    def save(self, *args, **kwargs):
        # Génération automatique du slug si absent
        if not self.slug:
            base_slug = slugify(self.titre) or f"article-{int(timezone.now().timestamp())}"
            slug = base_slug
            counter = 1
            while Actualite.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Calcul automatique du temps de lecture
        if self.contenu:
            nb_mots = len(self.contenu.split())
            self.temps_lecture = max(1, round(nb_mots / 200))

        # Si l'article passe à PUBLIE et n'a pas encore de date de publication
        if self.statut == self.Statut.PUBLIE and not self.date_publication:
            self.date_publication = timezone.now()

        super().save(*args, **kwargs)
