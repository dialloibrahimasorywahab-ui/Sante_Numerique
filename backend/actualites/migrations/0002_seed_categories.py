from django.db import migrations


def seed_categories(apps, schema_editor):
    CategorieActualite = apps.get_model('actualites', 'CategorieActualite')
    default_categories = [
        {
            'nom': "Vie de l'hôpital",
            'slug': "vie-de-l-hopital",
            'description': "Informations internes, nouveaux équipements, vie des services et personnels.",
            'couleur': "blue",
            'icone': "building",
            'actif': True
        },
        {
            'nom': "Santé et prévention",
            'slug': "sante-et-prevention",
            'description': "Sensibilisation, dépistage, bonnes pratiques d'hygiène et santé publique.",
            'couleur': "emerald",
            'icone': "shield",
            'actif': True
        },
        {
            'nom': "Conseils médicaux",
            'slug': "conseils-medicaux",
            'description': "Recommandations de nos praticiens pour prendre soin de votre santé au quotidien.",
            'couleur': "purple",
            'icone': "stethoscope",
            'actif': True
        },
        {
            'nom': "Événements",
            'slug': "evenements",
            'description': "Journées portes ouvertes, conférences médicales et colloques scientifiques.",
            'couleur': "amber",
            'icone': "calendar",
            'actif': True
        },
        {
            'nom': "Informations importantes",
            'slug': "informations-importantes",
            'description': "Avis urgents, consignes de sécurité et modifications d'horaires d'accueil.",
            'couleur': "rose",
            'icone': "alert",
            'actif': True
        },
    ]

    for cat in default_categories:
        CategorieActualite.objects.get_or_create(
            nom=cat['nom'],
            defaults=cat
        )


def unseed_categories(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('actualites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]

