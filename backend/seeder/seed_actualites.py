import os
import sys
import django
from django.utils import timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from actualites.models import CategorieActualite, Actualite
from users.models import User


CATEGORIES_DATA = [
    {
        "nom": "Vie de l'hôpital",
        "slug": "vie-de-l-hopital",
        "description": "Actualités internes, nouveaux équipements et vie quotidienne de notre complexe hospitalier.",
        "couleur": "emerald",
        "icone": "hospital",
    },
    {
        "nom": "Santé et prévention",
        "slug": "sante-et-prevention",
        "description": "Sensibilisation, campagnes de dépistage et bonnes pratiques pour préserver votre capital santé.",
        "couleur": "blue",
        "icone": "heart",
    },
    {
        "nom": "Conseils médicaux",
        "slug": "conseils-medicaux",
        "description": "Recommandations de nos praticiens spécialistes sur la gestion des pathologies et des traitements.",
        "couleur": "purple",
        "icone": "stethoscope",
    },
    {
        "nom": "Événements",
        "slug": "evenements",
        "description": "Journées portes ouvertes, conférences médicales, webinaires et congrès scientifiques.",
        "couleur": "amber",
        "icone": "calendar",
    },
    {
        "nom": "Informations importantes",
        "slug": "informations-importantes",
        "description": "Communiqués de la direction, protocoles d'accueil, horaires et consignes sanitaires.",
        "couleur": "red",
        "icone": "alert-circle",
    },
]

ARTICLES_DATA = [
    {
        "titre": "Inauguration du Nouveau Pôle d'Imagerie Médicale Haute Définition",
        "slug": "inauguration-nouveau-pole-imagerie-haute-definition",
        "categorie_slug": "vie-de-l-hopital",
        "resume": "Le Centre Hospitalier Santé Numérique se dote d'un équipement IRM 3 Tesla et d'un scanner spectral de dernière génération pour des diagnostics ultra-précis.",
        "contenu": """Le Centre Hospitalier Universitaire Santé Numérique franchit une étape majeure dans l'amélioration de son offre de soins avec l'inauguration officielle de son tout nouveau pôle d'imagerie médicale de pointe.

Doté d'une IRM 3 Tesla haute performance et d'un scanner spectral volumique, ce nouveau plateau technique permet de réduire considérablement la durée des examens tout en augmentant la résolution spatiale des acquisitions d'images. Les patients bénéficient ainsi d'un confort accru et d'une exposition aux rayonnements diminuée de plus de 40%.

« Cet investissement structurant permet à nos équipes de neurologie, d'oncologie et de cardiologie d'affiner leurs diagnostics de façon précoce et d'orienter les thérapies avec une exactitude sans précédent », a souligné la Direction Médicale lors de la cérémonie de coupure de ruban en présence des chefs de pôle.""",
        "image_url": "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80",
        "est_a_la_une": True,
        "temps_lecture": 4,
    },
    {
        "titre": "Journée Mondiale du Cœur : Adoptez les Réflexes qui Protègent vos Artères",
        "slug": "journee-mondiale-coeur-reflexes-protection-arteres",
        "categorie_slug": "sante-et-prevention",
        "resume": "La sédentarité et l'excès de sel restent les principaux facteurs de risque cardiovasculaire. Retrouvez le guide complet de nos cardiologues pour un cœur en pleine forme.",
        "contenu": """À l'occasion de la Journée Mondiale du Cœur, l'équipe du service de cardiologie de Santé Numérique rappelle les règles d'or pour prévenir les accidents vasculaires et l'infarctus du myocarde.

Une activité physique modérée de 30 minutes par jour (comme la marche rapide), une diminution sensible des aliments ultra-transformés et un suivi régulier de la pression artérielle après 40 ans suffisent à réduire de plus de 50% les risques d'accidents coronariens graves.

Nos équipes organisent ce jeudi des dépistages gratuits de l'hypertension et de la glycémie dans le hall central du bâtiment des consultations externes.""",
        "image_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=800&q=80",
        "est_a_la_une": False,
        "temps_lecture": 3,
    },
    {
        "titre": "Comment Bien Préparer sa Consultation chez le Spécialiste",
        "slug": "comment-bien-preparer-sa-consultation-specialiste",
        "categorie_slug": "conseils-medicaux",
        "resume": "Pour tirer le meilleur parti de votre rendez-vous médical, découvrez les documents indispensables à rassembler et les questions clés à poser à votre médecin.",
        "contenu": """Une consultation réussie se prépare en amont. Pour aider le praticien à poser le bon diagnostic rapidement, il est essentiel d'apporter l'ensemble de vos ordonnances en cours, vos derniers bilans sanguins et comptes-rendus d'examens d'imagerie.

Grâce à votre espace patient Santé Numérique, tous vos documents médicaux certifiés sont désormais archivés de façon sécurisée et directement consultables par vos médecins traitants lors de votre prise en charge.

Pensez également à noter par écrit vos symptômes, leur fréquence et les moments précis où ils apparaissent.""",
        "image_url": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=800&q=80",
        "est_a_la_une": False,
        "temps_lecture": 3,
    },
    {
        "titre": "Grand Séminaire Annuel : Les Nouvelles Approches en Télémédecine",
        "slug": "grand-seminaire-annuel-telemedecine-sante-numerique",
        "categorie_slug": "evenements",
        "resume": "Nos équipes soignantes et nos chercheurs partenaires se réunissent les 15 et 16 novembre prochains pour échanger sur l'apport de l'intelligence artificielle et du télé-suivi clinique.",
        "contenu": """Le CHU Santé Numérique accueille la 3ème édition du Colloque Régional sur l'Innovation en Santé Connectée. Plus de 200 praticiens, soignants et experts de l'informatique médicale sont attendus pour deux journées d'ateliers interactifs et de conférences plénières.

Les thématiques phares porteront sur la sécurisation des échanges de données de santé (chiffrement AES-256), le suivi ambulatoire des patients chroniques et la télésurveillance post-hospitalisation.""",
        "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80",
        "est_a_la_une": False,
        "temps_lecture": 5,
    },
    {
        "titre": "Mise à Jour des Protocoles d'Accueil et Horaires des Visites",
        "slug": "mise-a-jour-protocoles-accueil-horaires-visites",
        "categorie_slug": "informations-importantes",
        "resume": "Dans le but d'assurer un repos optimal aux patients hospitalisés tout en facilitant les visites des proches, les créneaux d'accès aux chambres ont été harmonisés.",
        "contenu": """La direction des soins informe les usagers et familles que les visites en service d'hospitalisation conventionnelle sont désormais ouvertes tous les jours de 13h00 à 19h30.

Pour les unités de soins intensifs et la réanimation, les visites restent limitées à deux personnes par créneau sur autorisation médicale préalable afin de respecter l'environnement calme requis pour les patients en phase critique.

Un accueil personnalisé avec distribution de badges numériques est à votre disposition dès l'entrée principale.""",
        "image_url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80",
        "est_a_la_une": False,
        "temps_lecture": 2,
    },
]


def run_seed_actualites():
    print("\n=========================================================")
    print("=== SEEDING DES ACTUALITÉS ET CONSEILS SANTÉ ===")
    print("=========================================================")

    admin_user = User.objects.filter(role=User.Role.ADMINISTRATEUR).first()

    # 1. Catégories
    categories_map = {}
    for cat_data in CATEGORIES_DATA:
        cat, created = CategorieActualite.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={
                "nom": cat_data["nom"],
                "description": cat_data["description"],
                "couleur": cat_data["couleur"],
                "icone": cat_data["icone"],
                "actif": True,
            }
        )
        categories_map[cat_data["slug"]] = cat
        status = "Créée" if created else "Existante"
        print(f" [Catégorie] {status} : {cat.nom} ({cat.slug})")

    # 2. Articles
    now = timezone.now()
    articles_created = 0

    for art_data in ARTICLES_DATA:
        cat = categories_map.get(art_data["categorie_slug"])
        if not cat:
            continue

        art = Actualite.objects.filter(slug=art_data["slug"]).first()
        if not art:
            art = Actualite.objects.create(
                titre=art_data["titre"],
                slug=art_data["slug"],
                categorie=cat,
                resume=art_data["resume"],
                contenu=art_data["contenu"],
                image_url=art_data["image_url"],
                auteur=admin_user,
                statut=Actualite.Statut.PUBLIE,
                est_a_la_une=art_data["est_a_la_une"],
                temps_lecture=art_data["temps_lecture"],
                date_publication=now,
            )
            articles_created += 1
            print(f" [Article] Créé : '{art.titre}' (À la une: {art.est_a_la_une})")
        else:
            art.categorie = cat
            art.resume = art_data["resume"]
            art.contenu = art_data["contenu"]
            art.image_url = art_data["image_url"]
            art.statut = Actualite.Statut.PUBLIE
            art.est_a_la_une = art_data["est_a_la_une"]
            art.date_publication = now
            art.save()
            print(f" [Article] Mis à jour : '{art.titre}' (À la une: {art.est_a_la_une})")

    print(f"\n[OK] Seeding actualités terminé ! Total en base : {Actualite.objects.count()} articles")
    print("=========================================================\n")


if __name__ == "__main__":
    run_seed_actualites()

