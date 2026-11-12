from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Perfil


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un Perfil cuando se crea un User."""
    if created:
        Perfil.objects.get_or_create(usuario=instance)