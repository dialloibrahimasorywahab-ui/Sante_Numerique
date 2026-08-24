from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Chambre


@receiver(post_save, sender=Chambre)
@receiver(post_delete, sender=Chambre)
def update_batiment_nombre_chambre(sender, instance, **kwargs):
    if instance.batiment:
        instance.batiment.sync_nombre_chambres()
