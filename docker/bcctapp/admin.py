from django.contrib import admin
from .models import Patient, Photo, MedicalImages, ImagesPatient, InteractionsPatient, Teams

# Register your models here.
admin.site.register(Patient)
admin.site.register(Photo)
admin.site.register(MedicalImages)
admin.site.register(ImagesPatient)
admin.site.register(InteractionsPatient)
admin.site.register(Teams)