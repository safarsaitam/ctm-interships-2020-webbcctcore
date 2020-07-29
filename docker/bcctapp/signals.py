from django.db.models.signals import post_save
from .models import Patient
from django.dispatch import receiver


@receiver(post_save,sender=Patient)
def add_image(sender,instance,created, **kwargs):
    if created:
        Patient.objects.create(image1=instance)


@receiver(post_save,sender=Patient)
def add_image(sender,instance, **kwargs):
    instance.patient.save()


