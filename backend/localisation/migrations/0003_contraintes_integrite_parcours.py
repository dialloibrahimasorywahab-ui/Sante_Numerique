# Migration : Ajout des contraintes d'intégrité PostgreSQL pour le parcours patient
# CORRECTION PROBLÈME 7
#
# RAPPORT D'ANOMALIES POTENTIELLES (à vérifier avant application en production) :
#
# 1. Contrainte "une seule localisation actuelle par séjour" :
#    Si des doublons existent (plusieurs localisations avec est_actuelle=True
#    pour un même séjour), la migration échouera sur PostgreSQL.
#    Stratégie de résolution : garder la localisation la plus récente (date_debut MAX),
#    mettre les autres à est_actuelle=False. À exécuter manuellement si nécessaire :
#
#    UPDATE localisation_localisationpatient SET est_actuelle = FALSE
#    WHERE id NOT IN (
#        SELECT DISTINCT ON (sejour_id) id
#        FROM localisation_localisationpatient
#        WHERE est_actuelle = TRUE
#        ORDER BY sejour_id, date_debut DESC
#    ) AND est_actuelle = TRUE;
#
# 2. Contrainte "un lit ne peut être occupé que par une seule localisation active" :
#    Si plusieurs localisations actives pointent vers le même lit, une seule sera
#    conservée avec est_actuelle=True. Vérifier avant migration :
#
#    SELECT lit_id, COUNT(*) FROM localisation_localisationpatient
#    WHERE est_actuelle = TRUE AND lit_id IS NOT NULL
#    GROUP BY lit_id HAVING COUNT(*) > 1;
#
# 3. La contrainte "un séjour actif par patient" est intentionnellement
#    NON ajoutée ici car la règle métier autorise potentiellement plusieurs
#    séjours actifs dans certains contextes (ex: transfert). À décider avec
#    le métier avant d'ajouter cette contrainte.
#
# NOTE : Cette migration est RÉVERSIBLE. En cas d'erreur, `migrate localisation 0002`
# restaure l'état précédent.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localisation', '0002_initial'),
    ]

    operations = [
        # Contrainte : une seule localisation actuelle par séjour
        # Utilise une contrainte unique partielle PostgreSQL (WHERE est_actuelle = TRUE)
        # Non supportée par SQLite — compatible PostgreSQL 12+ et Django 4+.
        migrations.AddConstraint(
            model_name='localisationpatient',
            constraint=models.UniqueConstraint(
                fields=['sejour'],
                condition=models.Q(est_actuelle=True),
                name='unique_localisation_actuelle_par_sejour',
            ),
        ),
        # Contrainte : un lit ne peut être attribué qu'à une seule localisation active
        # Empêche qu'un lit physique soit "occupé" par deux patients simultanément.
        migrations.AddConstraint(
            model_name='localisationpatient',
            constraint=models.UniqueConstraint(
                fields=['lit'],
                condition=models.Q(est_actuelle=True, lit__isnull=False),
                name='unique_lit_actif_par_localisation',
            ),
        ),
    ]

