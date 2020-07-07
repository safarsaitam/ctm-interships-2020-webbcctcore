from django import forms
from .models import CinderellaImages

class CinderellaImagesForm(forms.ModelForm):
    class Meta:
        model = CinderellaImages
        fields = ('before_image', 'image', 'age', 'weight', 'height', 'bra_size', )