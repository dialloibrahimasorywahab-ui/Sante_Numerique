from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lit


@receiver(post_save, sender=Lit)
@receiver(post_delete, sender=Lit)
def update_chambre_statut_on_lit_change(sender, instance, **kwargs):
    if instance.chambre:
        instance.chambre.sync_statut()
