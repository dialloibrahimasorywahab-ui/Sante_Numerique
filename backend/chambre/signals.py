from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Chambre


@receiver(post_save, sender=Chambre)
def update_batiment_on_chambre_save(sender, instance, created=False, update_fields=None, **kwargs):
    # Ne synchroniser le bâtiment que si une nouvelle chambre a été créée
    # ou si le rattachement de bâtiment a été modifié (évite les cascades d'écritures inutiles)
    if created or update_fields is None or 'batiment' in update_fields or 'id_batiment' in update_fields:
        if instance.batiment:
            instance.batiment.sync_nombre_chambres()


@receiver(post_delete, sender=Chambre)
def update_batiment_on_chambre_delete(sender, instance, **kwargs):
    if instance.batiment:
        instance.batiment.sync_nombre_chambres()
